"""Per-EA distributed trainer: N independent agents, one shared environment.

Each agent is a full DDQNTrainer (own online+target network, optimizer, replay,
epsilon schedule, target-sync counter). A multi-agent rollout drives one
calibrated environment and routes each task's decision + per-task delayed reward
to the owning EA's agent. Reuses the validated single-agent Double-DQN update
(_train_batch) and per-task credit assignment semantics. No proposed-method logic.
"""

from __future__ import annotations

import tempfile
from collections import deque
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from src.analysis.deadline_timeout_feasible_workload_calibration.calibration import (
    build_calibration_profile,
    patched_calibrated_environment,
)
from src.analysis.full_training_reproduction_campaign.config import TargetUpdateContract
from src.analysis.full_training_reproduction_campaign.replay import (
    ACTION_INDEX_TO_SEMANTICS,
    ReplayTransition,
    legal_action_mask_to_tuple,
    semantics_to_action_index,
)
from src.analysis.full_training_reproduction_campaign.trainer import (
    DDQNTrainer,
    EpsilonGreedyExploration,
    _build_environment,
)
from src.analysis.state_profile_decision_time_integration_recovery.state_profile_adapter import (
    build_profiled_campaign_config,
)

from .config import DistributedBaselineConfig


@contextmanager
def calibrated_environment():
    root = Path(tempfile.gettempdir()) / "per_ea_distributed_calibration"
    profile = build_calibration_profile(root)
    with patched_calibrated_environment(profile):
        yield


def _build_agent(cfg: DistributedBaselineConfig, *, epsilon_decay_episodes: int, seed_offset: int) -> DDQNTrainer:
    campaign_config = build_profiled_campaign_config(state_representation_profile=cfg.state_representation_profile)
    agent = DDQNTrainer(campaign_config)
    agent.exploration = EpsilonGreedyExploration(
        epsilon_start=cfg.epsilon_start,
        epsilon_final=cfg.epsilon_final,
        epsilon_decay_steps=epsilon_decay_episodes,
        decay_type="linear",
        schedule_unit="episode",
        seed=53 + seed_offset,
    )
    agent.per_task_credit_assignment = True
    agent.config.target_update_contract = TargetUpdateContract(
        update_frequency=cfg.target_update_frequency,
        target_update_unit="episode",
        approval_status="paper_aligned_episode_sync_approved",
        paper_evidence_status="ocr_recovered_algorithm_1_episode_copy",
    )
    return agent


class DistributedTrainer:
    def __init__(self, cfg: DistributedBaselineConfig, *, epsilon_decay_episodes: int) -> None:
        self.cfg = cfg
        self.episode_count = 0
        self.agents: list[DDQNTrainer] = [
            _build_agent(cfg, epsilon_decay_episodes=epsilon_decay_episodes, seed_offset=i)
            for i in range(cfg.num_agents)
        ]
        # template config (state profile / episode length) for env + eval reuse
        self.template_config = self.agents[0].config

    # --- structural accessors (for tests) ---
    def online_networks(self) -> list[Any]:
        return [a.online_network for a in self.agents]

    def target_networks(self) -> list[Any]:
        return [a.target_network for a in self.agents]

    def optimizers(self) -> list[Any]:
        return [a.optimizer for a in self.agents]

    def replay_buffers(self) -> list[Any]:
        return [a.replay_buffer for a in self.agents]

    def _owner(self, task) -> int:
        return int(getattr(task, "source_agent_id", 0)) % self.cfg.num_agents

    def _episode(self, episode_id: int, seed: int, *, training: bool) -> dict[str, Any]:
        episode_length = self.cfg.episode_length
        env = _build_environment(self.template_config, episode_length=episode_length, seed=seed)
        env.reset(seed=seed)
        histories = [a._initial_history(episode_length=episode_length) for a in self.agents]
        pending: dict[int, dict[str, Any]] = {}   # task_id -> {owner, skeleton}
        losses: list[float] = []
        per_agent_actions = [{"local": 0, "horizontal": 0, "vertical": 0} for _ in self.agents]
        finite = True

        def _train(owner: int) -> None:
            ag = self.agents[owner]
            if training and len(ag.replay_buffer) >= ag.config.batch_size:
                loss = ag._train_batch()
                losses.append(loss)

        while True:
            task = env.current_task
            owner = None
            action = None
            if task is not None:
                owner = self._owner(task)
                ag = self.agents[owner]
                obs = env.observe_flat(task)
                st, feat, window = ag._decision_state_tensor(
                    history=histories[owner], observation=obs, current_task=task, episode_length=episode_length,
                )
                legal = obs.get("legal_action_mask", {})
                greedy_idx = semantics_to_action_index(ag.policy.choose_action(st, legal))
                if training and ag.exploration is not None:
                    a_idx, _, _ = ag.exploration.select_action_index(
                        episode_id, greedy_idx, legal_action_mask_to_tuple(legal)
                    )
                else:
                    a_idx = greedy_idx
                action = ACTION_INDEX_TO_SEMANTICS[a_idx]
                if action in per_agent_actions[owner]:
                    per_agent_actions[owner][action] += 1

            next_obs, reward, terminated, truncated, info = env.step(action)
            finalized = info.get("finalized_tasks", [])

            if training and task is not None:
                from src.analysis.full_training_reproduction_campaign.replay import build_state_vector, build_state_window
                next_task = env.current_task
                nf = build_state_vector(
                    observation=env.observe_flat(next_task) if next_task is not None else (next_obs if isinstance(next_obs, dict) else {}),
                    current_task=next_task, episode_length=episode_length,
                    state_representation_profile=ag.config.state_representation_profile,
                )
                next_window = build_state_window(tuple(histories[owner]) + (feat, nf), state_representation_profile=ag.config.state_representation_profile)
                pending[int(getattr(task, "task_id", id(task)))] = {
                    "owner": owner, "state": window, "action": a_idx,
                    "legal": legal_action_mask_to_tuple(legal), "next_state": next_window,
                    "arrival_slot": int(getattr(task, "arrival_slot", 0)),
                    "agent_id": int(getattr(task, "source_agent_id", 0)),
                }
                histories[owner].append(feat)

            for ft in finalized:
                tid = int(ft.get("task_id", -1))
                sk = pending.pop(tid, None)
                if sk is None:
                    continue
                o = sk["owner"]
                ag = self.agents[o]
                outcome = ft.get("terminal_outcome")
                cslot = ft.get("completion_slot")
                if outcome == "completed" and cslot is not None:
                    r = -float(int(cslot) - sk["arrival_slot"] + 1)
                elif outcome == "dropped":
                    r = -float(getattr(ag.config, "drop_penalty", 40.0))
                else:
                    r = 0.0
                ag.replay_buffer.add(ReplayTransition(
                    state=sk["state"], action=sk["action"], legal_action_mask=sk["legal"],
                    next_state=sk["next_state"], reward=r,
                    reward_available=outcome in {"completed", "dropped"},
                    terminal=outcome in {"completed", "dropped"}, terminal_reason=outcome,
                    pending_at_horizon=False, arrival_slot=sk["arrival_slot"],
                    completion_or_drop_slot=int(cslot) if cslot is not None else None,
                    agent_id=sk["agent_id"], episode_id=episode_id, step_id=0,
                ))
                ag.per_task_credit_emitted += 1
                _train(o)

            if terminated or truncated:
                for sk in pending.values():
                    o = sk["owner"]; ag = self.agents[o]
                    ag.replay_buffer.add(ReplayTransition(
                        state=sk["state"], action=sk["action"], legal_action_mask=sk["legal"],
                        next_state=sk["next_state"], reward=0.0, reward_available=False,
                        terminal=False, terminal_reason="pending_at_horizon", pending_at_horizon=True,
                        arrival_slot=sk["arrival_slot"], completion_or_drop_slot=None,
                        agent_id=sk["agent_id"], episode_id=episode_id, step_id=0,
                    ))
                    ag.per_task_pending_flushed += 1
                    _train(o)
                pending.clear()
                break

        # per-agent episode-based target sync
        if training:
            for ag in self.agents:
                if ag.config.target_update_contract.target_update_unit == "episode" and \
                        ag.config.target_update_contract.should_sync(episode_count=episode_id + 1):
                    ag.target_network.load_state_dict(ag.online_network.state_dict())
                    ag.target_sync_count += 1
        for loss in losses:
            if loss != loss or loss in (float("inf"), float("-inf")):
                finite = False
        return {
            "loss_count": len(losses),
            "loss_value": losses[-1] if losses else 0.0,
            "loss_is_finite": finite,
            "per_agent_actions": per_agent_actions,
        }

    def train_to_budget(self, target_budget: int) -> dict[str, Any]:
        if target_budget < self.episode_count:
            raise ValueError("target_budget cannot move backwards")
        last = {"loss_is_finite": True, "loss_value": 0.0}
        with calibrated_environment():
            while self.episode_count < target_budget:
                seed = self.template_config.seed_bundle.training_trace_generation_seed + self.episode_count
                last = self._episode(self.episode_count, seed, training=True)
                self.episode_count += 1
        return {
            "training_budget": target_budget,
            "cumulative_episode_count": self.episode_count,
            "loss_is_finite": last["loss_is_finite"],
            "loss_value": last["loss_value"],
            "replay_sizes": [len(a.replay_buffer) for a in self.agents],
            "target_sync_counts": [a.target_sync_count for a in self.agents],
        }
