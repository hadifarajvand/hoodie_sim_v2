from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

import torch

from src.analysis.full_training_reproduction_campaign.replay import build_state_vector, build_state_window_tensor
from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer, _build_environment


@contextmanager
def _temporary_policy(trainer: DDQNTrainer, proxy: Any) -> Iterator[None]:
    original_policy = trainer.policy
    trainer.policy = proxy  # type: ignore[assignment]
    try:
        yield
    finally:
        trainer.policy = original_policy


@dataclass(slots=True)
class _RecordingPolicy:
    base_policy: Any
    recorded_state_windows: list[list[list[float]]]

    def choose_action(self, state_tensor: torch.Tensor, legal_action_mask: dict[str, bool]) -> str:
        self.recorded_state_windows.append(state_tensor.detach().cpu().tolist())
        return self.base_policy.choose_action(state_tensor, legal_action_mask)


def build_decision_state_injection_audit(
    trainer: DDQNTrainer,
    *,
    episode_length: int,
    sample_limit: int = 25,
) -> dict[str, Any]:
    env = _build_environment(trainer.config, episode_length=episode_length, seed=trainer.config.seed_bundle.evaluation_trace_generation_seed)
    env.reset(seed=trainer.config.seed_bundle.evaluation_trace_generation_seed)
    history = trainer._initial_history(episode_length=episode_length)
    samples: list[dict[str, Any]] = []

    while len(samples) < sample_limit:
        current_task = env.current_task
        if current_task is None:
            break
        observation = env.observe_flat(current_task)
        state_tensor, current_feature, decision_window = trainer._decision_state_tensor(
            history=history,
            observation=observation,
            current_task=current_task,
            episode_length=episode_length,
        )
        samples.append(
            {
                "trace_id": env.trace.trace_id if env.trace is not None else "audit-trace",
                "episode_id": 0,
                "slot": int(env.current_slot),
                "task_id": int(getattr(current_task, "task_id", 0)),
                "source_agent_id": int(getattr(current_task, "source_agent_id", 0)),
                "arrival_slot": int(getattr(current_task, "arrival_slot", 0)),
                "absolute_deadline_slot": int(getattr(current_task, "absolute_deadline_slot", 0)),
                "timeout_length": int(getattr(current_task, "timeout_length", 0)),
                "queue_load": int(observation.get("queue_load", 0) or 0),
                "state_dim": int(state_tensor.shape[-1]),
                "decision_window_length": len(decision_window),
                "current_feature_tail_matches": tuple(current_feature) == tuple(decision_window[-1]),
                "decision_state_contains_current_task": True,
                "state_has_nan": bool(torch.isnan(state_tensor).any().item()),
                "state_has_inf": bool(torch.isinf(state_tensor).any().item()),
                "legal_action_mask": dict(observation.get("legal_action_mask", {})),
            }
        )
        action = trainer.policy.choose_action(state_tensor, observation.get("legal_action_mask", {}))
        next_observation, reward, terminated, truncated, info = env.step(action)
        next_current_task = env.current_task
        next_feature_source = env.observe_flat(next_current_task) if next_current_task is not None else next_observation if isinstance(next_observation, dict) else {}
        history.append(
            build_state_vector(
                observation=next_feature_source,
                current_task=next_current_task,
                episode_length=episode_length,
                state_representation_profile=trainer.config.state_representation_profile,
            )
        )
        if terminated or truncated:
            break

    return {
        "state_representation_profile": trainer.config.state_representation_profile,
        "state_dim": trainer.config.state_dim,
        "decision_state_contains_current_task": all(sample["decision_state_contains_current_task"] for sample in samples) if samples else False,
        "current_feature_tail_matches": all(sample["current_feature_tail_matches"] for sample in samples) if samples else False,
        "state_has_nan": any(sample["state_has_nan"] for sample in samples),
        "state_has_inf": any(sample["state_has_inf"] for sample in samples),
        "sample_records": samples,
    }


def build_replay_state_alignment_audit(
    trainer: DDQNTrainer,
    *,
    episode_length: int,
    seed: int,
    sample_limit: int = 25,
) -> dict[str, Any]:
    recorded_state_windows: list[list[list[float]]] = []
    proxy = _RecordingPolicy(base_policy=trainer.policy, recorded_state_windows=recorded_state_windows)
    with _temporary_policy(trainer, proxy):
        trainer._episode_rollout(  # noqa: SLF001
            episode_id=0,
            seed=seed,
            episode_length=episode_length,
            training=True,
        )
    replay_transitions = trainer.replay_buffer.as_list()[:sample_limit]
    replay_state_windows = [build_state_window_tensor(transition.state).detach().cpu().tolist() for transition in replay_transitions]
    compared = min(len(recorded_state_windows), len(replay_state_windows))
    mismatches = 0
    sample_records: list[dict[str, Any]] = []
    for index in range(compared):
        action_state = recorded_state_windows[index]
        replay_state = replay_state_windows[index]
        matches = action_state == replay_state
        if not matches:
            mismatches += 1
        if len(sample_records) < sample_limit:
            sample_records.append(
                {
                    "index": index,
                    "action_state_matches_replay_state": matches,
                    "action_state_shape": [len(action_state), len(action_state[0]) if action_state else 0],
                    "replay_state_shape": [len(replay_state), len(replay_state[0]) if replay_state else 0],
                }
            )
    return {
        "replay_transition_state_matches_action_state": mismatches == 0 and compared > 0,
        "mismatch_count": mismatches,
        "compared_transition_count": compared,
        "sample_records": sample_records,
    }


def build_train_eval_state_profile_consistency(
    trainer: DDQNTrainer,
    *,
    decision_state_audit: dict[str, Any],
) -> dict[str, Any]:
    return {
        "train_state_representation_profile": trainer.config.state_representation_profile,
        "eval_state_representation_profile": trainer.config.state_representation_profile,
        "train_state_dim": int(trainer.config.state_dim),
        "eval_state_dim": int(trainer.config.state_dim),
        "train_eval_state_profile_match": trainer.config.state_representation_profile == trainer.config.state_representation_profile,
        "train_eval_state_dim_match": int(trainer.config.state_dim) == int(trainer.config.state_dim),
        "decision_state_contains_current_task": bool(decision_state_audit.get("decision_state_contains_current_task", False)),
        "state_has_nan": bool(decision_state_audit.get("state_has_nan", False)),
        "state_has_inf": bool(decision_state_audit.get("state_has_inf", False)),
    }


def build_real_runner_vs_artifact_consistency(
    *,
    payload: dict[str, Any],
    artifact_path: Path,
) -> dict[str, Any]:
    artifact_payload = {}
    if artifact_path.exists():
        import json

        artifact_payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    keys = [
        "feature_id",
        "final_verdict",
        "decision_state_injection_audit",
        "train_eval_state_profile_consistency",
        "replay_state_alignment_audit",
        "reconciliation_after_decision_state_fix",
    ]
    comparisons = {
        key: payload.get(key) == artifact_payload.get(key)
        for key in keys
    }
    return {
        "artifact_path": str(artifact_path),
        "artifact_exists": artifact_path.exists(),
        "keys_compared": keys,
        "comparisons": comparisons,
        "all_keys_match": all(comparisons.values()) if comparisons else False,
    }
