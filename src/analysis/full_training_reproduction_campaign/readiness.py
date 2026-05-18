from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from typing import Any

from src.environment.compute_config import ComputeConfig
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph

from .config import (
    CampaignConfig,
    READINESS_MANUAL_APPROVAL_APPROVED,
    READINESS_MANUAL_APPROVAL_NOT_APPROVED,
    READINESS_MANUAL_APPROVAL_REJECTED,
)
from .replay import build_state_vector, build_state_window, legal_action_mask_to_tuple, action_index_to_semantics


@dataclass(slots=True)
class ReadinessProbeResult:
    campaign_stage: str
    gate_status: str
    probe_episode_count: int
    probe_step_count: int
    generated_task_count: int
    transition_count: int
    completed_task_count: int
    dropped_task_count: int
    pending_at_horizon_count: int
    terminal_transition_count: int
    reward_bearing_transition_count: int
    non_terminal_transition_count: int
    terminal_transition_ratio: float
    reward_bearing_transition_ratio: float
    pending_at_horizon_ratio: float
    illegal_action_count: int
    illegal_action_ratio: float
    action_count_by_type: dict[str, int]
    local_action_count: int
    horizontal_action_count: int
    vertical_action_count: int
    readiness_manual_approval_required: bool
    readiness_manual_approval_status: str
    readiness_block_reason: str | None
    target_update_unit: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "probe_episode_count": self.probe_episode_count,
            "probe_step_count": self.probe_step_count,
            "generated_task_count": self.generated_task_count,
            "transition_count": self.transition_count,
            "completed_task_count": self.completed_task_count,
            "dropped_task_count": self.dropped_task_count,
            "pending_at_horizon_count": self.pending_at_horizon_count,
            "terminal_transition_count": self.terminal_transition_count,
            "reward_bearing_transition_count": self.reward_bearing_transition_count,
            "non_terminal_transition_count": self.non_terminal_transition_count,
            "terminal_transition_ratio": self.terminal_transition_ratio,
            "reward_bearing_transition_ratio": self.reward_bearing_transition_ratio,
            "pending_at_horizon_ratio": self.pending_at_horizon_ratio,
            "illegal_action_count": self.illegal_action_count,
            "illegal_action_ratio": self.illegal_action_ratio,
            "action_count_by_type": dict(self.action_count_by_type),
            "local_action_count": self.local_action_count,
            "horizontal_action_count": self.horizontal_action_count,
            "vertical_action_count": self.vertical_action_count,
            "readiness_manual_approval_required": self.readiness_manual_approval_required,
            "readiness_manual_approval_status": self.readiness_manual_approval_status,
            "readiness_block_reason": self.readiness_block_reason,
        }


class CampaignReadinessProbe:
    def __init__(self, config: CampaignConfig) -> None:
        self.config = config

    def _environment(self, *, seed: int) -> HoodieGymEnvironment:
        return HoodieGymEnvironment(
            episode_length=self.config.readiness_probe_episode_length,
            topology=TopologyGraph.from_approved_assumption_registry(),
            runtime_parameters=SharedRuntimeParameters(),
            compute_config=ComputeConfig(),
            policy_name="HOODIE",
        )

    def _choose_action(self, mask: dict[str, bool]) -> str:
        if mask.get("local", False):
            return "local"
        if mask.get("horizontal", False):
            return "horizontal"
        return "vertical"

    def run(self) -> ReadinessProbeResult:
        probe_episode_count = self.config.readiness_probe_episode_count
        probe_step_count = 0
        generated_task_count = 0
        transition_count = 0
        completed_task_count = 0
        dropped_task_count = 0
        pending_at_horizon_count = 0
        terminal_transition_count = 0
        reward_bearing_transition_count = 0
        non_terminal_transition_count = 0
        illegal_action_count = 0
        action_counter: Counter[str] = Counter()

        for episode_index in range(probe_episode_count):
            env = self._environment(seed=self.config.seed_bundle.readiness_probe_seed + episode_index)
            env.reset(seed=self.config.seed_bundle.readiness_probe_seed + episode_index)
            history = deque([build_state_vector(observation={"slot": 0, "queue_load": 0, "history_length": 0}, current_task=None, episode_length=self.config.readiness_probe_episode_length)] * 10, maxlen=10)
            while True:
                current_task = env.current_task
                if current_task is not None:
                    generated_task_count += 1
                    observation = env.observe_flat(current_task)
                    mask = observation.get("legal_action_mask", {})
                    action = self._choose_action(mask)
                    if not mask.get(action, False):
                        illegal_action_count += 1
                    action_counter[action] += 1
                else:
                    observation = env.observe_flat()
                    action = None

                state_window = build_state_window(history)
                next_observation, reward, terminated, truncated, info = env.step(action)
                probe_step_count += 1

                next_current_task = env.current_task
                next_feature = build_state_vector(
                    observation=env.observe_flat(next_current_task) if next_current_task is not None else next_observation if isinstance(next_observation, dict) else {},
                    current_task=next_current_task,
                    episode_length=self.config.readiness_probe_episode_length,
                )
                history.append(next_feature)

                finalized_tasks = info.get("finalized_tasks", [])
                if finalized_tasks:
                    terminal_transition_count += 1
                    reward_bearing_transition_count += 1
                    completed_task_count += sum(1 for task in finalized_tasks if task.get("terminal_outcome") == "completed")
                    dropped_task_count += sum(1 for task in finalized_tasks if task.get("terminal_outcome") == "dropped")
                if current_task is not None:
                    transition_count += 1
                    if not finalized_tasks:
                        non_terminal_transition_count += 1
                if truncated and (env.current_task is not None or info.get("queue_load", 0) > 0):
                    pending_at_horizon_count += 1

                if terminated or truncated:
                    break

        total_possible = max(transition_count, 1)
        readiness_manual_approval_required = True
        explicit_readiness_reference = self.config.readiness_manual_approval_reference.strip()
        requested_manual_approval = self.config.readiness_manual_approval_status
        has_terminal_exposure = terminal_transition_count > 0 and reward_bearing_transition_count > 0
        if requested_manual_approval == READINESS_MANUAL_APPROVAL_REJECTED:
            gate_status = "blocked"
            readiness_block_reason = "manual approval explicitly rejected"
            readiness_manual_approval_status = READINESS_MANUAL_APPROVAL_REJECTED
        elif requested_manual_approval == READINESS_MANUAL_APPROVAL_APPROVED and explicit_readiness_reference and has_terminal_exposure:
            gate_status = "pilot-ready"
            readiness_block_reason = None
            readiness_manual_approval_status = READINESS_MANUAL_APPROVAL_APPROVED
        elif not has_terminal_exposure:
            gate_status = "blocked"
            readiness_block_reason = "zero_reward_bearing_terminal_transitions"
            readiness_manual_approval_status = READINESS_MANUAL_APPROVAL_NOT_APPROVED
        elif requested_manual_approval == READINESS_MANUAL_APPROVAL_APPROVED and not explicit_readiness_reference:
            gate_status = "blocked"
            readiness_block_reason = "readiness_manual_approval_reference_missing"
            readiness_manual_approval_status = READINESS_MANUAL_APPROVAL_NOT_APPROVED
        else:
            gate_status = "blocked"
            readiness_block_reason = "manual approval required before campaign progression"
            readiness_manual_approval_status = READINESS_MANUAL_APPROVAL_NOT_APPROVED

        terminal_transition_ratio = terminal_transition_count / total_possible
        reward_bearing_transition_ratio = reward_bearing_transition_count / total_possible
        pending_at_horizon_ratio = pending_at_horizon_count / total_possible
        illegal_action_ratio = illegal_action_count / total_possible

        return ReadinessProbeResult(
            campaign_stage="readiness_probe",
            gate_status=gate_status,
            probe_episode_count=probe_episode_count,
            probe_step_count=probe_step_count,
            generated_task_count=generated_task_count,
            transition_count=transition_count,
            completed_task_count=completed_task_count,
            dropped_task_count=dropped_task_count,
            pending_at_horizon_count=pending_at_horizon_count,
            terminal_transition_count=terminal_transition_count,
            reward_bearing_transition_count=reward_bearing_transition_count,
            non_terminal_transition_count=non_terminal_transition_count,
            terminal_transition_ratio=terminal_transition_ratio,
            reward_bearing_transition_ratio=reward_bearing_transition_ratio,
            pending_at_horizon_ratio=pending_at_horizon_ratio,
            illegal_action_count=illegal_action_count,
            illegal_action_ratio=illegal_action_ratio,
            action_count_by_type=dict(action_counter),
            local_action_count=action_counter.get("local", 0),
            horizontal_action_count=action_counter.get("horizontal", 0),
            vertical_action_count=action_counter.get("vertical", 0),
            readiness_manual_approval_required=readiness_manual_approval_required,
            readiness_manual_approval_status=readiness_manual_approval_status,
            readiness_block_reason=readiness_block_reason,
            target_update_unit=self.config.target_update_contract.target_update_unit,
        )


def run_campaign_readiness_probe(config: CampaignConfig) -> ReadinessProbeResult:
    return CampaignReadinessProbe(config).run()
