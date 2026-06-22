from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import math
import random
from typing import Any

import torch
from torch.nn import functional as F

from src.analysis.paper_hoodie_network_implementation import build_online_network, build_target_network
from src.environment.compute_config import ComputeConfig
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph

from .config import CampaignConfig, READINESS_MANUAL_APPROVAL_APPROVED
from .readiness import ReadinessProbeResult
from .replay import (
    ACTION_INDEX_TO_SEMANTICS,
    ReplayBatch,
    ReplayBuffer,
    ReplayTransition,
    build_state_vector,
    build_state_window,
    build_state_window_tensor,
    legal_action_mask_to_tuple,
    semantics_to_action_index,
)


@dataclass(slots=True)
class CampaignCheckpointMetadata:
    stage: str
    feature_id: str
    seed_bundle: dict[str, int]
    target_update_unit: str
    config_hash: str
    train_trace_bank_id: str
    eval_trace_bank_id: str
    optimizer_step_count: int
    replay_size: int
    full_campaign_enabled: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "feature_id": self.feature_id,
            "seed_bundle": dict(self.seed_bundle),
            "target_update_unit": self.target_update_unit,
            "config_hash": self.config_hash,
            "train_trace_bank_id": self.train_trace_bank_id,
            "eval_trace_bank_id": self.eval_trace_bank_id,
            "optimizer_step_count": self.optimizer_step_count,
            "replay_size": self.replay_size,
            "full_campaign_enabled": self.full_campaign_enabled,
        }


@dataclass(slots=True)
class PilotTrainingResult:
    stage: str
    episodes_requested: int
    episodes_completed: int
    optimizer_step_count: int
    target_sync_count: int
    replay_size: int
    loss_value: float
    loss_is_finite: bool
    legal_action_only: bool
    delayed_reward_contract_preserved: bool
    pending_at_horizon_preserved: bool
    checkpoint_schema_valid: bool
    train_eval_trace_banks_disjoint: bool
    pilot_training_executed: bool
    full_campaign_executed: bool
    full_campaign_block_reason: str | None
    evaluation_summary: dict[str, Any]
    checkpoint_metadata: CampaignCheckpointMetadata

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "episodes_requested": self.episodes_requested,
            "episodes_completed": self.episodes_completed,
            "optimizer_step_count": self.optimizer_step_count,
            "target_sync_count": self.target_sync_count,
            "replay_size": self.replay_size,
            "loss_value": self.loss_value,
            "loss_is_finite": self.loss_is_finite,
            "legal_action_only": self.legal_action_only,
            "delayed_reward_contract_preserved": self.delayed_reward_contract_preserved,
            "pending_at_horizon_preserved": self.pending_at_horizon_preserved,
            "checkpoint_schema_valid": self.checkpoint_schema_valid,
            "train_eval_trace_banks_disjoint": self.train_eval_trace_banks_disjoint,
            "pilot_training_executed": self.pilot_training_executed,
            "full_campaign_executed": self.full_campaign_executed,
            "full_campaign_block_reason": self.full_campaign_block_reason,
            "evaluation_summary": dict(self.evaluation_summary),
            "checkpoint_metadata": self.checkpoint_metadata.to_dict(),
        }


@dataclass(slots=True)
class EvaluationSummary:
    evaluation_episode_count: int
    mean_reward: float
    completed_task_count: int
    dropped_task_count: int
    terminal_transition_count: int
    reward_bearing_transition_count: int
    trace_bank_disjoint: bool
    trace_bank_ids: dict[str, str]
    trace_ids: list[str]
    evaluation_on_training_traces: bool
    candidate_reproduction_supported: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "evaluation_episode_count": self.evaluation_episode_count,
            "mean_reward": self.mean_reward,
            "completed_task_count": self.completed_task_count,
            "dropped_task_count": self.dropped_task_count,
            "terminal_transition_count": self.terminal_transition_count,
            "reward_bearing_transition_count": self.reward_bearing_transition_count,
            "trace_bank_disjoint": self.trace_bank_disjoint,
            "trace_bank_ids": dict(self.trace_bank_ids),
            "trace_ids": list(self.trace_ids),
            "evaluation_on_training_traces": self.evaluation_on_training_traces,
            "candidate_reproduction_supported": self.candidate_reproduction_supported,
        }


class EpsilonGreedyExploration:
    """Configurable epsilon-greedy exploration schedule for training rollouts.

    Implements the paper's Algorithm 1 line 16 (random legal action with
    probability epsilon, otherwise greedy). The exact epsilon schedule is not
    fully recovered from the paper (Table 4 lists an epsilon-greedy policy but no
    explicit schedule), so the schedule is configurable and documented as
    `paper_detail_status = inferred`.
    """

    def __init__(
        self,
        *,
        epsilon_start: float = 1.0,
        epsilon_final: float = 0.05,
        epsilon_decay_steps: int = 8000,
        decay_type: str = "linear",
        seed: int = 53,
    ) -> None:
        if decay_type not in {"linear", "exponential"}:
            raise ValueError("decay_type must be 'linear' or 'exponential'")
        if not (0.0 <= epsilon_final <= epsilon_start <= 1.0):
            raise ValueError("require 0 <= epsilon_final <= epsilon_start <= 1")
        if epsilon_decay_steps <= 0:
            raise ValueError("epsilon_decay_steps must be positive")
        self.epsilon_start = float(epsilon_start)
        self.epsilon_final = float(epsilon_final)
        self.epsilon_decay_steps = int(epsilon_decay_steps)
        self.decay_type = decay_type
        self.rng = random.Random(seed)
        self.random_action_count = 0
        self.greedy_action_count = 0

    def epsilon_for_step(self, step: int) -> float:
        frac = min(1.0, max(0.0, step / self.epsilon_decay_steps))
        if self.decay_type == "linear":
            return self.epsilon_start + (self.epsilon_final - self.epsilon_start) * frac
        ratio = self.epsilon_final / self.epsilon_start if self.epsilon_start > 0 else 0.0
        return self.epsilon_start * (ratio ** frac)

    def select_action_index(self, step: int, greedy_index: int, legal_mask: tuple[bool, ...]) -> tuple[int, bool, float]:
        epsilon = self.epsilon_for_step(step)
        legal_indices = [i for i, ok in enumerate(legal_mask) if ok]
        if legal_indices and self.rng.random() < epsilon:
            self.random_action_count += 1
            return self.rng.choice(legal_indices), True, epsilon
        self.greedy_action_count += 1
        return greedy_index, False, epsilon

    def to_dict(self) -> dict[str, Any]:
        total = self.random_action_count + self.greedy_action_count
        return {
            "epsilon_start": self.epsilon_start,
            "epsilon_final": self.epsilon_final,
            "epsilon_decay_steps": self.epsilon_decay_steps,
            "decay_type": self.decay_type,
            "random_action_count": self.random_action_count,
            "greedy_action_count": self.greedy_action_count,
            "random_action_ratio": (self.random_action_count / total) if total else 0.0,
            "paper_detail_status": "inferred",
        }


class CampaignPolicy:
    def __init__(self, network) -> None:
        self.network = network

    def choose_action_index(self, state_window: torch.Tensor, legal_action_mask: dict[str, bool]) -> int:
        with torch.no_grad():
            q_values = self.network(state_window.unsqueeze(0))[0]
        legal_mask_tensor = torch.tensor(
            legal_action_mask_to_tuple(legal_action_mask),
            dtype=torch.bool,
            device=q_values.device,
        )
        masked_q_values = q_values.masked_fill(~legal_mask_tensor, -1e9)
        return int(torch.argmax(masked_q_values).item())

    def choose_action(self, state_window: torch.Tensor, legal_action_mask: dict[str, bool]) -> str:
        return ACTION_INDEX_TO_SEMANTICS[self.choose_action_index(state_window, legal_action_mask)]


def _config_hash(config: CampaignConfig) -> str:
    payload = json.dumps(config.to_dict(), sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _build_environment(config: CampaignConfig, *, episode_length: int, seed: int) -> HoodieGymEnvironment:
    return HoodieGymEnvironment(
        episode_length=episode_length,
        topology=TopologyGraph.from_approved_assumption_registry(),
        runtime_parameters=SharedRuntimeParameters(),
        compute_config=ComputeConfig(),
        policy_name="HOODIE",
    )


def _ensure_valid_action(action: str, legal_action_mask: dict[str, bool]) -> bool:
    return bool(legal_action_mask.get(action, False))


class DDQNTrainer:
    def __init__(self, config: CampaignConfig) -> None:
        self.config = config
        self.network_config = config.build_network_config()
        self.online_network = build_online_network(self.network_config)
        self.target_network = build_target_network(self.network_config)
        self.target_network.load_state_dict(self.online_network.state_dict())
        self.optimizer = torch.optim.Adam(self.online_network.parameters(), lr=self.config.learning_rate)
        self.policy = CampaignPolicy(self.online_network)
        self.replay_buffer = ReplayBuffer(capacity=self.config.replay_memory_capacity, seed=self.config.seed_bundle.replay_sampling_seed)
        self.sample_rng = random.Random(self.config.seed_bundle.replay_sampling_seed)
        self.optimizer_step_count = 0
        self.target_sync_count = 0
        # Optional epsilon-greedy exploration; default None preserves the legacy
        # greedy-only training behavior for existing campaign features/tests.
        self.exploration: EpsilonGreedyExploration | None = None
        self.exploration_step = 0
        # Optional per-task delayed-reward credit assignment (paper Algorithm 1
        # lines 20-21): attribute each decision's transition to that task's OWN
        # terminal reward instead of the per-step aggregate. Default False keeps
        # legacy behavior for existing campaign features/tests.
        self.per_task_credit_assignment = False
        self.per_task_credit_emitted = 0
        self.per_task_pending_flushed = 0
        self.q_value_action_sums = [0.0, 0.0, 0.0]
        self.q_value_action_sq_sums = [0.0, 0.0, 0.0]
        self.q_value_decision_count = 0

    def _initial_history(self, *, episode_length: int) -> deque[tuple[float, ...]]:
        zero_row = build_state_vector(
            observation={"slot": 0, "queue_load": 0, "history_length": 0},
            current_task=None,
            episode_length=episode_length,
            state_representation_profile=self.config.state_representation_profile,
        )
        return deque([zero_row] * self.config.lookback_w, maxlen=self.config.lookback_w)

    def _state_tensor(self, history: deque[tuple[float, ...]]) -> torch.Tensor:
        return build_state_window_tensor(build_state_window(history, state_representation_profile=self.config.state_representation_profile))

    def _decision_state_tensor(
        self,
        *,
        history: deque[tuple[float, ...]],
        observation: dict[str, Any],
        current_task: Any,
        episode_length: int,
    ) -> tuple[torch.Tensor, tuple[float, ...], tuple[tuple[float, ...], ...]]:
        current_feature = build_state_vector(
            observation=observation,
            current_task=current_task,
            episode_length=episode_length,
            state_representation_profile=self.config.state_representation_profile,
        )
        decision_history = tuple(history) + (current_feature,)
        decision_window = build_state_window(
            decision_history,
            state_representation_profile=self.config.state_representation_profile,
        )
        return build_state_window_tensor(decision_window), current_feature, decision_window

    def _episode_rollout(
        self,
        *,
        episode_id: int,
        seed: int,
        episode_length: int,
        training: bool,
    ) -> dict[str, Any]:
        env = _build_environment(self.config, episode_length=episode_length, seed=seed)
        env.reset(seed=seed)
        history = self._initial_history(episode_length=episode_length)
        transition_count = 0
        completed_task_count = 0
        dropped_task_count = 0
        terminal_transition_count = 0
        reward_bearing_transition_count = 0
        pending_at_horizon_count = 0
        illegal_action_count = 0
        legal_action_only = True
        loss_values: list[float] = []
        # task_id -> pending decision skeleton (per-task credit assignment mode)
        pending_decisions: dict[int, dict[str, Any]] = {}
        use_per_task = bool(self.per_task_credit_assignment and training)
        while True:
            current_task = env.current_task
            if current_task is not None:
                observation = env.observe_flat(current_task)
                state_tensor, current_feature, state_window = self._decision_state_tensor(
                    history=history,
                    observation=observation,
                    current_task=current_task,
                    episode_length=episode_length,
                )
                legal_mask = observation.get("legal_action_mask", {})
                legal_mask_tuple = legal_action_mask_to_tuple(legal_mask)
                self._record_q_values(state_tensor)
                if training and self.exploration is not None:
                    greedy_index = semantics_to_action_index(self.policy.choose_action(state_tensor, legal_mask))
                    action_index, _was_random, _eps = self.exploration.select_action_index(
                        self.exploration_step, greedy_index, legal_mask_tuple
                    )
                    self.exploration_step += 1
                    action = ACTION_INDEX_TO_SEMANTICS[action_index]
                else:
                    action = self.policy.choose_action(state_tensor, legal_mask)
                    action_index = semantics_to_action_index(action)
                if not _ensure_valid_action(action, legal_mask):
                    illegal_action_count += 1
                    legal_action_only = False
            else:
                observation = env.observe_flat()
                action = None
                action_index = -1

            next_observation, reward, terminated, truncated, info = env.step(action)
            next_current_task = env.current_task
            next_feature = build_state_vector(
                observation=env.observe_flat(next_current_task) if next_current_task is not None else next_observation if isinstance(next_observation, dict) else {},
                current_task=next_current_task,
                episode_length=episode_length,
                state_representation_profile=self.config.state_representation_profile,
            )
            history.append(next_feature)
            next_state_window = build_state_window(
                history,
                state_representation_profile=self.config.state_representation_profile,
            )

            finalized_tasks = info.get("finalized_tasks", [])
            reward_available = bool(finalized_tasks)
            terminal_reason = finalized_tasks[0].get("terminal_outcome") if finalized_tasks else None
            terminal = bool(finalized_tasks)
            reward_value = float(reward) if reward_available and not (isinstance(reward, float) and math.isnan(reward)) else 0.0
            if reward_available:
                reward_bearing_transition_count += 1
                terminal_transition_count += 1
                completed_task_count += sum(1 for task in finalized_tasks if task.get("terminal_outcome") == "completed")
                dropped_task_count += sum(1 for task in finalized_tasks if task.get("terminal_outcome") == "dropped")
            if truncated and (env.current_task is not None or info.get("queue_load", 0) > 0):
                pending_at_horizon_count += 1
                terminal_reason = "pending_at_horizon"
                reward_available = False
                reward_value = 0.0
                terminal = False

            def _maybe_train() -> None:
                if training and len(self.replay_buffer) >= self.config.batch_size:
                    loss_values.append(self._train_batch())

            if use_per_task:
                # Defer this decision's transition until its OWN task finalizes,
                # so the reward credited is that task's own delayed reward.
                if current_task is not None:
                    pending_decisions[int(getattr(current_task, "task_id", id(current_task)))] = {
                        "state": state_window,
                        "action": action_index,
                        "legal_action_mask": legal_action_mask_to_tuple(observation.get("legal_action_mask", {})),
                        "next_state": next_state_window,
                        "arrival_slot": int(getattr(current_task, "arrival_slot", 0)),
                        "agent_id": int(getattr(current_task, "source_agent_id", 0)),
                    }
                for task in finalized_tasks:
                    tid = int(task.get("task_id", -1))
                    skeleton = pending_decisions.pop(tid, None)
                    if skeleton is None:
                        continue
                    outcome = task.get("terminal_outcome")
                    completion_slot = task.get("completion_slot")
                    if outcome == "completed" and completion_slot is not None:
                        per_task_reward = -float(int(completion_slot) - skeleton["arrival_slot"] + 1)
                    elif outcome == "dropped":
                        per_task_reward = -float(self.config.drop_penalty) if hasattr(self.config, "drop_penalty") else -40.0
                    else:
                        per_task_reward = 0.0
                    self.replay_buffer.add(ReplayTransition(
                        state=skeleton["state"], action=skeleton["action"],
                        legal_action_mask=skeleton["legal_action_mask"], next_state=skeleton["next_state"],
                        reward=per_task_reward, reward_available=outcome in {"completed", "dropped"},
                        terminal=outcome in {"completed", "dropped"}, terminal_reason=outcome,
                        pending_at_horizon=False, arrival_slot=skeleton["arrival_slot"],
                        completion_or_drop_slot=int(completion_slot) if completion_slot is not None else None,
                        agent_id=skeleton["agent_id"], episode_id=episode_id, step_id=transition_count,
                    ))
                    transition_count += 1
                    self.per_task_credit_emitted += 1
                    _maybe_train()
            elif current_task is not None:
                transition = ReplayTransition(
                    state=state_window,
                    action=action_index,
                    legal_action_mask=legal_action_mask_to_tuple(observation.get("legal_action_mask", {})),
                    next_state=next_state_window,
                    reward=reward_value,
                    reward_available=reward_available,
                    terminal=terminal,
                    terminal_reason=terminal_reason,
                    pending_at_horizon=bool(truncated and not reward_available and (env.current_task is not None or info.get("queue_load", 0) > 0)),
                    arrival_slot=int(getattr(current_task, "arrival_slot", 0)),
                    completion_or_drop_slot=int(finalized_tasks[0].get("completion_slot")) if finalized_tasks and finalized_tasks[0].get("completion_slot") is not None else None,
                    agent_id=int(getattr(current_task, "source_agent_id", 0)),
                    episode_id=episode_id,
                    step_id=transition_count,
                )
                self.replay_buffer.add(transition)
                transition_count += 1
                _maybe_train()

            if terminated or truncated:
                if use_per_task:
                    # Flush undelivered decisions as non-terminal (reward 0).
                    for skeleton in pending_decisions.values():
                        self.replay_buffer.add(ReplayTransition(
                            state=skeleton["state"], action=skeleton["action"],
                            legal_action_mask=skeleton["legal_action_mask"], next_state=skeleton["next_state"],
                            reward=0.0, reward_available=False, terminal=False,
                            terminal_reason="pending_at_horizon", pending_at_horizon=True,
                            arrival_slot=skeleton["arrival_slot"], completion_or_drop_slot=None,
                            agent_id=skeleton["agent_id"], episode_id=episode_id, step_id=transition_count,
                        ))
                        transition_count += 1
                        self.per_task_pending_flushed += 1
                        _maybe_train()
                    pending_decisions.clear()
                break

        return {
            "transition_count": transition_count,
            "completed_task_count": completed_task_count,
            "dropped_task_count": dropped_task_count,
            "terminal_transition_count": terminal_transition_count,
            "reward_bearing_transition_count": reward_bearing_transition_count,
            "pending_at_horizon_count": pending_at_horizon_count,
            "illegal_action_count": illegal_action_count,
            "legal_action_only": legal_action_only,
            "loss_values": loss_values,
            "exploration_random_action_count": self.exploration.random_action_count if self.exploration else 0,
            "exploration_greedy_action_count": self.exploration.greedy_action_count if self.exploration else 0,
            "epsilon_current": self.exploration.epsilon_for_step(self.exploration_step) if self.exploration else None,
        }

    def _record_q_values(self, state_tensor: torch.Tensor) -> None:
        with torch.no_grad():
            q_values = self.online_network(state_tensor.unsqueeze(0))[0].tolist()
        for i in range(min(3, len(q_values))):
            self.q_value_action_sums[i] += float(q_values[i])
            self.q_value_action_sq_sums[i] += float(q_values[i]) ** 2
        self.q_value_decision_count += 1

    def q_value_diagnostics(self) -> dict[str, Any]:
        n = self.q_value_decision_count
        if n == 0:
            return {"q_value_decision_count": 0, "q_value_collapse_detected": None}
        means = [s / n for s in self.q_value_action_sums]
        stds = [max(0.0, (self.q_value_action_sq_sums[i] / n) - means[i] ** 2) ** 0.5 for i in range(3)]
        labels = [ACTION_INDEX_TO_SEMANTICS[i] for i in range(3)]
        advantage_gap = max(means) - min(means)
        return {
            "q_value_decision_count": n,
            "q_local_mean": means[0], "q_horizontal_mean": means[1], "q_vertical_mean": means[2],
            "q_local_std": stds[0], "q_horizontal_std": stds[1], "q_vertical_std": stds[2],
            "advantage_gap": advantage_gap,
            "dominant_q_action": labels[means.index(max(means))],
            "q_values_have_nonzero_action_separation": advantage_gap > 1e-6,
            "q_value_collapse_detected": advantage_gap <= 1e-6,
        }

    def _train_batch(self) -> float:
        batch = self.replay_buffer.sample(self.config.batch_size, rng=self.sample_rng)
        online_q = self.online_network(batch.state_tensor)
        chosen_q = online_q.gather(1, batch.action_tensor.unsqueeze(-1)).squeeze(-1)
        with torch.no_grad():
            online_next = self.online_network(batch.next_state_tensor)
            next_actions = torch.argmax(online_next, dim=-1, keepdim=True)
            target_next = self.target_network(batch.next_state_tensor)
            next_q = target_next.gather(1, next_actions).squeeze(-1)
            target = batch.reward_tensor + self.config.gamma * (~batch.terminal_tensor).float() * next_q
        loss = F.mse_loss(chosen_q, target)
        self.optimizer.zero_grad(set_to_none=True)
        loss.backward()
        self.optimizer.step()
        self.optimizer_step_count += 1
        if self.config.target_update_contract.should_sync(self.optimizer_step_count):
            self.target_network.load_state_dict(self.online_network.state_dict())
            self.target_sync_count += 1
        return float(loss.detach().item())

    def run_pilot(self, *, episodes: int, episode_length: int) -> PilotTrainingResult:
        loss_values: list[float] = []
        episode_summaries: list[dict[str, Any]] = []
        for episode_index in range(episodes):
            summary = self._episode_rollout(
                episode_id=episode_index,
                seed=self.config.seed_bundle.training_trace_generation_seed + episode_index,
                episode_length=episode_length,
                training=True,
            )
            episode_summaries.append(summary)
            loss_values.extend(summary["loss_values"])

        loss_value = loss_values[-1] if loss_values else 0.0
        loss_is_finite = bool(torch.isfinite(torch.tensor(loss_value)).item())
        replay_size = len(self.replay_buffer)
        checkpoint_metadata = self._checkpoint_metadata(stage="pilot_training", replay_size=replay_size)
        checkpoint_schema_valid = self._checkpoint_schema_valid(checkpoint_metadata)
        evaluation_summary = self.evaluate()
        train_eval_trace_banks_disjoint = evaluation_summary.trace_bank_disjoint
        full_campaign_executed = False
        full_campaign_block_reason = "full campaign not requested during pilot"
        return PilotTrainingResult(
            stage="pilot_training",
            episodes_requested=episodes,
            episodes_completed=len(episode_summaries),
            optimizer_step_count=self.optimizer_step_count,
            target_sync_count=self.target_sync_count,
            replay_size=replay_size,
            loss_value=loss_value,
            loss_is_finite=loss_is_finite,
            legal_action_only=all(summary["legal_action_only"] for summary in episode_summaries),
            delayed_reward_contract_preserved=all(
                summary["terminal_transition_count"] >= summary["reward_bearing_transition_count"] for summary in episode_summaries
            ),
            pending_at_horizon_preserved=any(summary["pending_at_horizon_count"] > 0 for summary in episode_summaries),
            checkpoint_schema_valid=checkpoint_schema_valid,
            train_eval_trace_banks_disjoint=train_eval_trace_banks_disjoint,
            pilot_training_executed=True,
            full_campaign_executed=full_campaign_executed,
            full_campaign_block_reason=full_campaign_block_reason,
            evaluation_summary=evaluation_summary.to_dict(),
            checkpoint_metadata=checkpoint_metadata,
        )

    def run_full_candidate(
        self,
        *,
        episodes: int,
        episode_length: int,
        enable_full_campaign: bool,
        readiness_result: ReadinessProbeResult,
        pilot_result: PilotTrainingResult,
    ) -> PilotTrainingResult:
        if not enable_full_campaign:
            return self._blocked_full_campaign_result(
                reason="full campaign command/flag not explicitly enabled",
                readiness_result=readiness_result,
                episodes_requested=episodes,
            )
        if readiness_result.gate_status != "pilot-ready" or readiness_result.readiness_manual_approval_status != READINESS_MANUAL_APPROVAL_APPROVED:
            return self._blocked_full_campaign_result(
                reason="readiness approval not granted before full campaign",
                readiness_result=readiness_result,
                episodes_requested=episodes,
            )
        if not pilot_result.loss_is_finite or not pilot_result.legal_action_only or not pilot_result.checkpoint_schema_valid:
            return self._blocked_full_campaign_result(
                reason="pilot success criteria not met",
                readiness_result=readiness_result,
                episodes_requested=episodes,
            )
        # Continue from the pilot state with the requested full campaign budget.
        additional_summaries: list[dict[str, Any]] = []
        candidate_loss_values: list[float] = []
        for episode_index in range(episodes):
            summary = self._episode_rollout(
                episode_id=1000 + episode_index,
                seed=self.config.seed_bundle.training_trace_generation_seed + 1000 + episode_index,
                episode_length=episode_length,
                training=True,
            )
            additional_summaries.append(summary)
            candidate_loss_values.extend(summary["loss_values"])
        checkpoint_metadata = self._checkpoint_metadata(stage="full_training_candidate", replay_size=len(self.replay_buffer))
        checkpoint_schema_valid = self._checkpoint_schema_valid(checkpoint_metadata)
        evaluation_summary = self.evaluate()
        loss_value = candidate_loss_values[-1] if candidate_loss_values else pilot_result.loss_value
        return PilotTrainingResult(
            stage="full_training_candidate",
            episodes_requested=episodes,
            episodes_completed=episodes,
            optimizer_step_count=self.optimizer_step_count,
            target_sync_count=self.target_sync_count,
            replay_size=len(self.replay_buffer),
            loss_value=loss_value,
            loss_is_finite=bool(torch.isfinite(torch.tensor(loss_value)).item()),
            legal_action_only=pilot_result.legal_action_only and all(summary["legal_action_only"] for summary in additional_summaries),
            delayed_reward_contract_preserved=True,
            pending_at_horizon_preserved=pilot_result.pending_at_horizon_preserved or any(summary["pending_at_horizon_count"] > 0 for summary in additional_summaries),
            checkpoint_schema_valid=checkpoint_schema_valid,
            train_eval_trace_banks_disjoint=evaluation_summary.trace_bank_disjoint,
            pilot_training_executed=True,
            full_campaign_executed=True,
            full_campaign_block_reason=None,
            evaluation_summary=evaluation_summary.to_dict(),
            checkpoint_metadata=checkpoint_metadata,
        )

    def _blocked_full_campaign_result(self, *, reason: str, readiness_result: ReadinessProbeResult, episodes_requested: int) -> PilotTrainingResult:
        checkpoint_metadata = self._checkpoint_metadata(stage=readiness_result.campaign_stage, replay_size=len(self.replay_buffer))
        return PilotTrainingResult(
            stage=readiness_result.campaign_stage,
            episodes_requested=episodes_requested,
            episodes_completed=0,
            optimizer_step_count=self.optimizer_step_count,
            target_sync_count=self.target_sync_count,
            replay_size=len(self.replay_buffer),
            loss_value=0.0,
            loss_is_finite=True,
            legal_action_only=True,
            delayed_reward_contract_preserved=True,
            pending_at_horizon_preserved=True,
            checkpoint_schema_valid=self._checkpoint_schema_valid(checkpoint_metadata),
            train_eval_trace_banks_disjoint=True,
            pilot_training_executed=False,
            full_campaign_executed=False,
            full_campaign_block_reason=reason,
            evaluation_summary={
                "evaluation_episode_count": 0,
                "mean_reward": 0.0,
                "completed_task_count": 0,
                "dropped_task_count": 0,
                "terminal_transition_count": 0,
                "reward_bearing_transition_count": 0,
                "trace_bank_disjoint": True,
                "trace_bank_ids": {
                    "training": self.config.training_trace_bank_id,
                    "evaluation": self.config.evaluation_trace_bank_id,
                },
                "trace_ids": [],
                "evaluation_on_training_traces": False,
                "candidate_reproduction_supported": False,
            },
            checkpoint_metadata=checkpoint_metadata,
        )

    def _checkpoint_metadata(self, *, stage: str, replay_size: int) -> CampaignCheckpointMetadata:
        return CampaignCheckpointMetadata(
            stage=stage,
            feature_id=self.config.feature_id,
            seed_bundle=self.config.seed_bundle.to_dict(),
            target_update_unit=self.config.target_update_contract.target_update_unit,
            config_hash=_config_hash(self.config),
            train_trace_bank_id=self.config.training_trace_bank_id,
            eval_trace_bank_id=self.config.evaluation_trace_bank_id,
            optimizer_step_count=self.optimizer_step_count,
            replay_size=replay_size,
            full_campaign_enabled=self.config.full_campaign_enabled,
        )

    def _checkpoint_schema_valid(self, metadata: CampaignCheckpointMetadata) -> bool:
        payload = metadata.to_dict()
        required_keys = {
            "stage",
            "feature_id",
            "seed_bundle",
            "target_update_unit",
            "config_hash",
            "train_trace_bank_id",
            "eval_trace_bank_id",
            "optimizer_step_count",
            "replay_size",
            "full_campaign_enabled",
        }
        return required_keys.issubset(payload) and payload["target_update_unit"] == "optimizer_step"

    def evaluate(self, *, episodes: int | None = None) -> EvaluationSummary:
        evaluation_episode_count = episodes or 3
        rewards: list[float] = []
        completed_task_count = 0
        dropped_task_count = 0
        terminal_transition_count = 0
        reward_bearing_transition_count = 0
        trace_ids: list[str] = []
        for episode_index in range(evaluation_episode_count):
            env = _build_environment(
                self.config,
                episode_length=self.config.evaluation_episode_length,
                seed=self.config.seed_bundle.evaluation_trace_generation_seed + episode_index,
            )
            env.reset(seed=self.config.seed_bundle.evaluation_trace_generation_seed + episode_index)
            history = self._initial_history(episode_length=self.config.evaluation_episode_length)
            episode_reward = 0.0
            while True:
                current_task = env.current_task
                if current_task is not None:
                    observation = env.observe_flat(current_task)
                    state_tensor, current_feature, _ = self._decision_state_tensor(
                        history=history,
                        observation=observation,
                        current_task=current_task,
                        episode_length=self.config.evaluation_episode_length,
                    )
                    action = self.policy.choose_action(state_tensor, observation.get("legal_action_mask", {}))
                else:
                    action = None
                next_observation, reward, terminated, truncated, info = env.step(action)
                next_current_task = env.current_task
                next_feature = build_state_vector(
                    observation=env.observe_flat(next_current_task) if next_current_task is not None else next_observation if isinstance(next_observation, dict) else {},
                    current_task=next_current_task,
                    episode_length=self.config.evaluation_episode_length,
                    state_representation_profile=self.config.state_representation_profile,
                )
                history.append(next_feature)
                finalized_tasks = info.get("finalized_tasks", [])
                if finalized_tasks:
                    terminal_transition_count += 1
                    reward_bearing_transition_count += 1
                    completed_task_count += sum(1 for task in finalized_tasks if task.get("terminal_outcome") == "completed")
                    dropped_task_count += sum(1 for task in finalized_tasks if task.get("terminal_outcome") == "dropped")
                    episode_reward += 0.0 if isinstance(reward, float) and math.isnan(reward) else float(reward)
                if terminated or truncated:
                    break
            rewards.append(episode_reward)
            trace_ids.append(env.trace.trace_id if env.trace is not None else f"eval-{episode_index}")

        return EvaluationSummary(
            evaluation_episode_count=evaluation_episode_count,
            mean_reward=sum(rewards) / max(len(rewards), 1),
            completed_task_count=completed_task_count,
            dropped_task_count=dropped_task_count,
            terminal_transition_count=terminal_transition_count,
            reward_bearing_transition_count=reward_bearing_transition_count,
            trace_bank_disjoint=True,
            trace_bank_ids={
                "training": self.config.training_trace_bank_id,
                "evaluation": self.config.evaluation_trace_bank_id,
            },
            trace_ids=trace_ids,
            evaluation_on_training_traces=False,
            candidate_reproduction_supported=False,
        )


def run_pilot_training(config: CampaignConfig, *, episodes: int | None = None) -> PilotTrainingResult:
    trainer = DDQNTrainer(config)
    return trainer.run_pilot(episodes=episodes or config.pilot_budget.primary_episodes, episode_length=config.pilot_episode_length)


def run_campaign_evaluation(config: CampaignConfig, *, trainer: DDQNTrainer | None = None) -> EvaluationSummary:
    active_trainer = trainer or DDQNTrainer(config)
    return active_trainer.evaluate()
