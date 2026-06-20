from __future__ import annotations

from collections import Counter, defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
import math
import random
from typing import Any, Callable, Iterator

import torch

from src.analysis.full_training_reproduction_campaign.config import CampaignConfig
from src.analysis.full_training_reproduction_campaign.replay import build_state_vector
from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer, _build_environment
from src.environment.reward_timing import phi_private

from .config import EVALUATION_ACTION_SEQUENCE_SAMPLE_LIMIT, EvaluationInstrumentationDiagnosticConfig

PolicyFn = Callable[[torch.Tensor, dict[str, bool], dict[str, Any]], str]


def normalize_action_name(action: str | None) -> str | None:
    if action is None:
        return None
    mapping = {
        "compute_local": "local",
        "offload_horizontal": "horizontal",
        "offload_vertical": "vertical",
    }
    return mapping.get(action, action)


def action_order() -> tuple[str, str, str]:
    return ("local", "horizontal", "vertical")


def mask_signature(mask: dict[str, bool]) -> str:
    return "|".join(f"{action}={int(bool(mask.get(action, False)))}" for action in action_order())


def terminal_reward_from_task_dict(task: dict[str, Any], *, drop_penalty: float = 40.0) -> float:
    terminal_outcome = task.get("terminal_outcome")
    if terminal_outcome == "completed" and task.get("completion_slot") is not None:
        return -float(phi_private(int(task["completion_slot"]), int(task["arrival_slot"])))
    if terminal_outcome == "dropped":
        return -float(drop_penalty)
    raise ValueError("Reward is only defined for completed or dropped tasks")


def terminal_latency_slots(task: dict[str, Any]) -> int | None:
    completion_slot = task.get("completion_slot")
    arrival_slot = task.get("arrival_slot")
    if completion_slot is None or arrival_slot is None:
        return None
    return int(completion_slot) - int(arrival_slot) + 1


def _empty_action_bucket() -> dict[str, Any]:
    return {
        "decision_count": 0,
        "completed_count": 0,
        "dropped_count": 0,
        "pending_at_horizon_count": 0,
        "terminal_transition_count": 0,
        "reward_bearing_transition_count": 0,
        "total_reward": 0.0,
        "mean_reward": 0.0,
        "completion_reward_count": 0,
        "drop_penalty_count": 0,
        "mean_completion_latency_slots": None,
        "mean_drop_latency_slots": None,
        "_completion_latency_sum": 0.0,
        "_completion_latency_count": 0,
        "_drop_latency_sum": 0.0,
        "_drop_latency_count": 0,
    }


def _finalize_action_bucket(bucket: dict[str, Any]) -> dict[str, Any]:
    reward_count = bucket["terminal_transition_count"]
    bucket["mean_reward"] = bucket["total_reward"] / reward_count if reward_count else 0.0
    bucket["mean_completion_latency_slots"] = (
        bucket["_completion_latency_sum"] / bucket["_completion_latency_count"] if bucket["_completion_latency_count"] else None
    )
    bucket["mean_drop_latency_slots"] = bucket["_drop_latency_sum"] / bucket["_drop_latency_count"] if bucket["_drop_latency_count"] else None
    bucket.pop("_completion_latency_sum", None)
    bucket.pop("_completion_latency_count", None)
    bucket.pop("_drop_latency_sum", None)
    bucket.pop("_drop_latency_count", None)
    return bucket


def _empty_reward_decomposition() -> dict[str, Any]:
    action_terminal = {
        action: {
            "completed": {"count": 0, "total_reward": 0.0, "mean_reward": 0.0},
            "dropped": {"count": 0, "total_reward": 0.0, "mean_reward": 0.0},
        }
        for action in action_order()
    }
    return {
        "reward_by_action": {action: 0.0 for action in action_order()},
        "reward_by_terminal_outcome": {"completed": 0.0, "dropped": 0.0},
        "reward_by_action_and_terminal_outcome": action_terminal,
        "drop_penalty_count_by_action": {action: 0 for action in action_order()},
        "completion_reward_count_by_action": {action: 0 for action in action_order()},
        "nan_reward_count": 0,
        "zero_reward_count": 0,
        "reward_available_count": 0,
    }


def _finalize_reward_decomposition(decomposition: dict[str, Any]) -> dict[str, Any]:
    for action in action_order():
        for outcome in ("completed", "dropped"):
            bucket = decomposition["reward_by_action_and_terminal_outcome"][action][outcome]
            bucket["mean_reward"] = bucket["total_reward"] / bucket["count"] if bucket["count"] else 0.0
    return decomposition


def _build_training_reward_summary(transitions: list[Any]) -> dict[str, Any]:
    rewards = [float(transition.reward) for transition in transitions if getattr(transition, "reward_available", False)]
    pending_at_horizon_count = sum(1 for transition in transitions if getattr(transition, "pending_at_horizon", False))
    return {
        "reward_count": len(rewards),
        "total_reward": float(sum(rewards)) if rewards else 0.0,
        "mean_reward": float(sum(rewards) / len(rewards)) if rewards else 0.0,
        "pending_at_horizon_count": pending_at_horizon_count,
    }


def _build_replay_window_action_distribution(transitions: list[Any]) -> dict[str, int]:
    counts = Counter({action: 0 for action in action_order()})
    for transition in transitions:
        action = {0: "local", 1: "horizontal", 2: "vertical"}.get(int(getattr(transition, "action", -1)))
        if action in counts:
            counts[action] += 1
    return dict(counts)


def _build_action_counts_from_records(records: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter({action: 0 for action in action_order()})
    for record in records:
        action = normalize_action_name(record.get("action"))
        if action in counts:
            counts[action] += 1
    return dict(counts)


def _episode_seed(config: CampaignConfig, episode_index: int) -> int:
    return config.seed_bundle.training_trace_generation_seed + episode_index


def _evaluation_seed(config: CampaignConfig, episode_index: int) -> int:
    return config.seed_bundle.evaluation_trace_generation_seed + episode_index


@dataclass
class _TrainingActionLogger:
    episode_id: int | None = None
    seed: int | None = None
    records: list[dict[str, Any]] = None  # type: ignore[assignment]

    def begin_episode(self, *, episode_id: int, seed: int) -> None:
        self.episode_id = episode_id
        self.seed = seed
        self.records = []

    def record(self, *, step_id: int, action: str, legal_action_mask: dict[str, bool], state_tensor: torch.Tensor) -> None:
        del state_tensor
        self.records.append(
            {
                "episode_id": self.episode_id,
                "seed": self.seed,
                "step_id": step_id,
                "action": action,
                "legal_action_mask": dict(legal_action_mask),
            }
        )

    def snapshot(self) -> list[dict[str, Any]]:
        return list(self.records or [])


class _LoggingPolicyProxy:
    def __init__(self, base_policy: Any, logger: _TrainingActionLogger) -> None:
        self.base_policy = base_policy
        self.logger = logger
        self._step_id = 0

    def begin_episode(self) -> None:
        self._step_id = 0

    def choose_action(self, state_tensor: torch.Tensor, legal_action_mask: dict[str, bool]) -> str:
        action = self.base_policy.choose_action(state_tensor, legal_action_mask)
        self.logger.record(step_id=self._step_id, action=action, legal_action_mask=legal_action_mask, state_tensor=state_tensor)
        self._step_id += 1
        return action


@contextmanager
def _temporary_policy(trainer: DDQNTrainer, proxy: _LoggingPolicyProxy) -> Iterator[None]:
    original_policy = trainer.policy
    trainer.policy = proxy  # type: ignore[assignment]
    try:
        yield
    finally:
        trainer.policy = original_policy


class InstrumentedTrainingSession:
    def __init__(self, config: EvaluationInstrumentationDiagnosticConfig) -> None:
        self.config = config
        self.campaign_config = CampaignConfig(
            evaluation_episode_length=config.episode_length,
            full_campaign_episode_length=config.episode_length,
        )
        self.trainer = DDQNTrainer(self.campaign_config)
        self.training_episode_count = 0
        self.loss_values: list[float] = []
        self.cumulative_training_action_distribution: Counter[str] = Counter({action: 0 for action in action_order()})
        self.cumulative_reward_total = 0.0
        self.cumulative_reward_count = 0
        self.cumulative_pending_at_horizon_count = 0
        self._training_logger = _TrainingActionLogger()
        self._policy_proxy = _LoggingPolicyProxy(self.trainer.policy, self._training_logger)

    def train_to_budget(self, target_budget: int) -> dict[str, Any]:
        if target_budget < self.training_episode_count:
            raise ValueError("target_budget cannot move backwards")
        while self.training_episode_count < target_budget:
            episode_id = self.training_episode_count
            seed = _episode_seed(self.campaign_config, episode_id)
            before_replay_size = len(self.trainer.replay_buffer)
            self._training_logger.begin_episode(episode_id=episode_id, seed=seed)
            self._policy_proxy.begin_episode()
            with _temporary_policy(self.trainer, self._policy_proxy):
                rollout_summary = self.trainer._episode_rollout(  # noqa: SLF001 - reuse the existing trainer semantics without modifying them
                    episode_id=episode_id,
                    seed=seed,
                    episode_length=self.config.episode_length,
                    training=True,
                )
            action_records = self._training_logger.snapshot()
            new_transitions = self.trainer.replay_buffer.as_list()[before_replay_size:]
            episode_action_distribution = _build_action_counts_from_records(action_records)
            self.cumulative_training_action_distribution.update(episode_action_distribution)
            reward_summary = _build_training_reward_summary(new_transitions)
            self.cumulative_reward_total += reward_summary["total_reward"]
            self.cumulative_reward_count += reward_summary["reward_count"]
            self.cumulative_pending_at_horizon_count += reward_summary["pending_at_horizon_count"]
            self.loss_values.extend(float(loss) for loss in rollout_summary["loss_values"])
            self.training_episode_count += 1
        replay_window_action_distribution = _build_replay_window_action_distribution(self.trainer.replay_buffer.as_list())
        return {
            "training_budget": target_budget,
            "cumulative_training_episode_count": self.training_episode_count,
            "optimizer_step_count": self.trainer.optimizer_step_count,
            "replay_size": len(self.trainer.replay_buffer),
            "loss_count": len(self.loss_values),
            "last_loss": float(self.loss_values[-1]) if self.loss_values else None,
            "loss_finite": bool(math.isfinite(float(self.loss_values[-1]))) if self.loss_values else True,
            "reward_summary": {
                "reward_count": self.cumulative_reward_count,
                "total_reward": float(self.cumulative_reward_total),
                "mean_reward": float(self.cumulative_reward_total / self.cumulative_reward_count) if self.cumulative_reward_count else 0.0,
                "pending_at_horizon_count": self.cumulative_pending_at_horizon_count,
            },
            "replay_window_action_distribution": replay_window_action_distribution,
            "replay_window_is_full_training_history": False,
            "replay_window_capacity": 10_000,
            "replay_window_interpretation_warning": True,
            "cumulative_training_action_distribution": dict(self.cumulative_training_action_distribution),
            "training_action_sequence_sample": self._training_logger.snapshot()[: EVALUATION_ACTION_SEQUENCE_SAMPLE_LIMIT],
        }

    def _candidate_policy_fn(self) -> PolicyFn:
        def _choose(state_tensor: torch.Tensor, legal_action_mask: dict[str, bool], context: dict[str, Any]) -> str:
            del context
            return self.trainer.policy.choose_action(state_tensor, legal_action_mask)

        return _choose

    def candidate_policy_result(self, *, checkpoint_budget: int) -> dict[str, Any]:
        return evaluate_policy_on_trace_bank(
            trainer=self.trainer,
            policy_name=f"candidate_policy_at_{checkpoint_budget}",
            policy_fn=self._candidate_policy_fn(),
            evaluation_episode_count=self.config.evaluation_episode_count_per_checkpoint,
            episode_length=self.config.episode_length,
            seed_base=self.campaign_config.seed_bundle.evaluation_trace_generation_seed,
            checkpoint_budget=checkpoint_budget,
            policy_kind="candidate",
        )


def _policy_random_legal(rng: random.Random, legal_action_mask: dict[str, bool]) -> str:
    legal_actions = [action for action in action_order() if legal_action_mask.get(action, False)]
    if not legal_actions:
        raise ValueError("No legal actions available")
    return rng.choice(legal_actions)


def build_fixed_policy_suite(seed: int) -> dict[str, PolicyFn]:
    del seed
    local_action = "local"
    horizontal_action = "horizontal"
    vertical_action = "vertical"

    def _fixed_action(action: str) -> PolicyFn:
        def _choose(state_tensor: torch.Tensor, legal_action_mask: dict[str, bool], context: dict[str, Any]) -> str:
            del state_tensor, context
            if legal_action_mask.get(action, False):
                return action
            for fallback in action_order():
                if legal_action_mask.get(fallback, False):
                    return fallback
            raise ValueError("No legal action available")

        return _choose

    def _random_legal(state_tensor: torch.Tensor, legal_action_mask: dict[str, bool], context: dict[str, Any]) -> str:
        del state_tensor
        episode_rng: random.Random = context["rng"]
        return _policy_random_legal(episode_rng, legal_action_mask)

    return {
        "fixed_local_policy": _fixed_action(local_action),
        "fixed_horizontal_policy": _fixed_action(horizontal_action),
        "fixed_vertical_policy": _fixed_action(vertical_action),
        "random_legal_policy": _random_legal,
    }


def build_policy_effect_diagnostic(
    *,
    trainer: DDQNTrainer,
    checkpoint_results: list[dict[str, Any]],
    fixed_policy_seed: int,
    evaluation_episode_count: int,
    episode_length: int,
    evaluation_trace_bank_id: str,
) -> dict[str, Any]:
    policy_results: dict[str, Any] = {}
    candidate_means: list[float] = []
    candidate_action_distributions: list[dict[str, int]] = []
    candidate_terminal_outcomes: list[tuple[int, int, int]] = []
    for checkpoint in checkpoint_results:
        budget = int(checkpoint["training_budget"])
        candidate_key = f"candidate_policy_at_{budget}"
        candidate_result = dict(checkpoint["evaluation_policy_result"])
        candidate_result["evaluation_trace_bank_id"] = evaluation_trace_bank_id
        policy_results[candidate_key] = candidate_result
        candidate_means.append(float(candidate_result["mean_reward"]))
        candidate_action_distributions.append(dict(candidate_result["evaluation_action_distribution"]))
        candidate_terminal_outcomes.append(
            (
                int(candidate_result["completed_count"]),
                int(candidate_result["dropped_count"]),
                int(candidate_result["pending_at_horizon_count"]),
            )
        )

    fixed_policies = build_fixed_policy_suite(fixed_policy_seed)
    for policy_name, policy_fn in fixed_policies.items():
        policy_results[policy_name] = evaluate_policy_on_trace_bank(
            trainer=trainer,
            policy_name=policy_name,
            policy_fn=policy_fn,
            evaluation_episode_count=evaluation_episode_count,
            episode_length=episode_length,
            seed_base=trainer.config.seed_bundle.evaluation_trace_generation_seed,
            policy_kind="fixed",
            evaluation_trace_bank_id=evaluation_trace_bank_id,
        )

    mean_reward_variance = max(candidate_means) - min(candidate_means) if candidate_means else 0.0
    action_distribution_changed = len({tuple(result["evaluation_action_distribution"].items()) for result in policy_results.values()}) > 1
    terminal_outcomes_changed = len({(result["completed_count"], result["dropped_count"], result["pending_at_horizon_count"]) for result in policy_results.values()}) > 1
    candidate_reward_static = mean_reward_variance <= 1e-9
    candidate_checkpoint_key = f"candidate_policy_at_{checkpoint_results[-1]['training_budget']}" if checkpoint_results else None
    candidate_vertical_collapse = (
        float(policy_results[candidate_checkpoint_key]["evaluation_action_distribution"].get("vertical", 0))
        / max(float(policy_results[candidate_checkpoint_key]["evaluation_decision_count"]), 1.0)
        >= 0.95
    ) if candidate_checkpoint_key is not None else False

    reward_same_across_policies = len({round(float(result["mean_reward"]), 9) for result in policy_results.values()}) == 1
    terminal_same_across_policies = len({(result["completed_count"], result["dropped_count"], result["pending_at_horizon_count"]) for result in policy_results.values()}) == 1

    policy_affects_reward = "true" if not reward_same_across_policies else "false"
    policy_affects_terminal_outcomes = "true" if not terminal_same_across_policies else "false"
    evaluation_metric_static_because_policy_same = "false"
    if reward_same_across_policies and action_distribution_changed:
        evaluation_metric_static_because_reward_aggregation = "true"
    elif reward_same_across_policies:
        evaluation_metric_static_because_reward_aggregation = "uncertain"
    else:
        evaluation_metric_static_because_reward_aggregation = "false"
    evaluation_metric_static_because_environment_dynamics = "true" if reward_same_across_policies and terminal_same_across_policies else "uncertain"

    return {
        "evaluation_trace_bank_id": evaluation_trace_bank_id,
        "evaluation_episode_count": evaluation_episode_count,
        "episode_length": episode_length,
        "candidate_policy_vertical_collapse_in_evaluation": candidate_vertical_collapse,
        "candidate_policy_vertical_collapse_in_training_replay_window": (
            float(checkpoint_results[-1]["training_state"]["replay_window_action_distribution"].get("vertical", 0))
            / max(float(checkpoint_results[-1]["training_state"]["replay_size"]), 1.0)
            >= 0.95
        ) if checkpoint_results else False,
        "policy_affects_reward": policy_affects_reward,
        "policy_affects_terminal_outcomes": policy_affects_terminal_outcomes,
        "evaluation_metric_static_because_policy_same": evaluation_metric_static_because_policy_same,
        "evaluation_metric_static_because_reward_aggregation": evaluation_metric_static_because_reward_aggregation,
        "evaluation_metric_static_because_environment_dynamics": evaluation_metric_static_because_environment_dynamics,
        "evaluation_reward_static_after_instrumentation": candidate_reward_static,
        "policy_results": policy_results,
        "candidate_reward_variation": mean_reward_variance,
        "candidate_action_distribution_changed_by_budget": len({tuple(result["evaluation_action_distribution"].items()) for key, result in policy_results.items() if key.startswith("candidate_policy_at_")}) > 1,
        "candidate_terminal_outcomes_changed_by_budget": len({(result["completed_count"], result["dropped_count"], result["pending_at_horizon_count"]) for key, result in policy_results.items() if key.startswith("candidate_policy_at_")}) > 1,
    }


def evaluate_policy_on_trace_bank(
    *,
    trainer: DDQNTrainer,
    policy_name: str,
    policy_fn: PolicyFn,
    evaluation_episode_count: int,
    episode_length: int,
    seed_base: int,
    checkpoint_budget: int | None = None,
    policy_kind: str = "candidate",
    evaluation_trace_bank_id: str | None = None,
) -> dict[str, Any]:
    evaluation_action_distribution: Counter[str] = Counter({action: 0 for action in action_order()})
    evaluation_legal_action_mask_distribution: Counter[str] = Counter()
    evaluation_action_by_trace_id: dict[str, Any] = {}
    evaluation_action_by_episode_id: dict[str, Any] = {}
    action_sequence_sample: list[dict[str, Any]] = []
    per_action_outcome_summary = {action: _empty_action_bucket() for action in action_order()}
    reward_decomposition = _empty_reward_decomposition()
    trace_ids: list[str] = []
    rewards: list[float] = []
    completed_total = 0
    dropped_total = 0
    pending_total = 0
    terminal_transition_count = 0
    reward_bearing_transition_count = 0
    decision_count = 0
    step_reward_nan_count = 0
    step_reward_zero_count = 0
    completion_latency_sum_total = 0.0
    completion_latency_count_total = 0
    drop_latency_sum_total = 0.0
    drop_latency_count_total = 0

    for episode_index in range(evaluation_episode_count):
        seed = seed_base + episode_index
        env = _build_environment(trainer.config, episode_length=episode_length, seed=seed)
        env.reset(seed=seed)
        history = trainer._initial_history(episode_length=episode_length)
        episode_reward = 0.0
        episode_action_distribution: Counter[str] = Counter({action: 0 for action in action_order()})
        episode_completed = 0
        episode_dropped = 0
        episode_pending = 0
        episode_terminal_transition_count = 0
        episode_reward_bearing_transition_count = 0
        episode_records: list[dict[str, Any]] = []

        step_index = 0
        while True:
            current_task = env.current_task
            current_action: str | None = None
            legal_action_mask = {}
            if current_task is not None:
                observation = env.observe_flat(current_task)
                legal_action_mask = dict(observation.get("legal_action_mask", {}))
                state_tensor = trainer._state_tensor(history)
                context = {
                    "episode_index": episode_index,
                    "episode_seed": seed,
                    "step_index": step_index,
                    "trace_id": env.trace.trace_id if env.trace is not None else f"eval-{episode_index}",
                    "rng": random.Random(seed * 10_000 + step_index),
                    "policy_name": policy_name,
                    "policy_kind": policy_kind,
                }
                current_action = normalize_action_name(policy_fn(state_tensor, legal_action_mask, context))
                if current_action not in evaluation_action_distribution:
                    current_action = normalize_action_name(current_action) or current_action
                evaluation_action_distribution[current_action] += 1
                episode_action_distribution[current_action] += 1
                decision_count += 1
                mask_key = mask_signature(legal_action_mask)
                evaluation_legal_action_mask_distribution[mask_key] += 1
                record = {
                    "episode_id": episode_index,
                    "trace_id": env.trace.trace_id if env.trace is not None else f"eval-{episode_index}",
                    "step_id": step_index,
                    "action": current_action,
                    "legal_action_mask": legal_action_mask,
                    "policy_name": policy_name,
                    "policy_kind": policy_kind,
                }
                if len(action_sequence_sample) < EVALUATION_ACTION_SEQUENCE_SAMPLE_LIMIT:
                    action_sequence_sample.append(record)
                episode_records.append(record)
            next_observation, reward, terminated, truncated, info = env.step(current_action)
            next_current_task = env.current_task
            next_feature_source = env.observe_flat(next_current_task) if next_current_task is not None else next_observation if isinstance(next_observation, dict) else {}
            next_feature = build_state_vector(
                observation=next_feature_source,
                current_task=next_current_task,
                episode_length=episode_length,
            )
            history.append(next_feature)
            finalized_tasks = info.get("finalized_tasks", [])
            if math.isnan(float(reward)):
                step_reward_nan_count += 1
            elif float(reward) == 0.0:
                step_reward_zero_count += 1

            if finalized_tasks:
                terminal_transition_count += len(finalized_tasks)
                reward_bearing_transition_count += len(finalized_tasks)
                episode_terminal_transition_count += len(finalized_tasks)
                episode_reward_bearing_transition_count += len(finalized_tasks)
                for task in finalized_tasks:
                    action = normalize_action_name(task.get("selected_action")) or "local"
                    outcome = task.get("terminal_outcome")
                    task_reward = terminal_reward_from_task_dict(task)
                    task_latency = terminal_latency_slots(task)
                    reward_decomposition["reward_available_count"] += 1
                    reward_decomposition["reward_by_action"][action] += task_reward
                    reward_decomposition["reward_by_terminal_outcome"][outcome] += task_reward
                    reward_bucket = reward_decomposition["reward_by_action_and_terminal_outcome"][action][outcome]
                    reward_bucket["count"] += 1
                    reward_bucket["total_reward"] += task_reward
                    if outcome == "completed":
                        reward_decomposition["completion_reward_count_by_action"][action] += 1
                        completed_total += 1
                        episode_completed += 1
                        if task_latency is not None:
                            bucket = per_action_outcome_summary[action]
                            bucket["_completion_latency_sum"] += task_latency
                            bucket["_completion_latency_count"] += 1
                            completion_latency_sum_total += task_latency
                            completion_latency_count_total += 1
                    elif outcome == "dropped":
                        reward_decomposition["drop_penalty_count_by_action"][action] += 1
                        dropped_total += 1
                        episode_dropped += 1
                        if task_latency is not None:
                            bucket = per_action_outcome_summary[action]
                            bucket["_drop_latency_sum"] += task_latency
                            bucket["_drop_latency_count"] += 1
                            drop_latency_sum_total += task_latency
                            drop_latency_count_total += 1
                    bucket = per_action_outcome_summary[action]
                    bucket["terminal_transition_count"] += 1
                    bucket["reward_bearing_transition_count"] += 1
                    bucket["total_reward"] += task_reward
                    if outcome == "completed":
                        bucket["completed_count"] += 1
                    elif outcome == "dropped":
                        bucket["dropped_count"] += 1
                    episode_reward += task_reward
            if truncated and (env.current_task is not None or info.get("queue_load", 0) > 0):
                pending_total += 1
                episode_pending += 1
                if current_action is not None:
                    bucket = per_action_outcome_summary[current_action]
                    bucket["pending_at_horizon_count"] += 1
            if current_action is not None:
                per_action_outcome_summary[current_action]["decision_count"] += 1
            if terminated or truncated:
                break
            step_index += 1

        rewards.append(episode_reward)
        trace_id = env.trace.trace_id if env.trace is not None else f"eval-{episode_index}"
        trace_ids.append(trace_id)
        episode_action_distribution_dict = dict(episode_action_distribution)
        evaluation_action_by_trace_id[trace_id] = {
            "episode_id": episode_index,
            "trace_id": trace_id,
            "decision_count": sum(episode_action_distribution_dict.values()),
            "action_distribution": episode_action_distribution_dict,
            "completed_count": episode_completed,
            "dropped_count": episode_dropped,
            "pending_at_horizon_count": episode_pending,
            "terminal_transition_count": episode_terminal_transition_count,
            "reward_bearing_transition_count": episode_reward_bearing_transition_count,
            "episode_reward": episode_reward,
            "policy_name": policy_name,
            "policy_kind": policy_kind,
        }
        evaluation_action_by_episode_id[str(episode_index)] = dict(evaluation_action_by_trace_id[trace_id])

    for bucket in per_action_outcome_summary.values():
        _finalize_action_bucket(bucket)
    _finalize_reward_decomposition(reward_decomposition)
    mean_reward = sum(rewards) / max(len(rewards), 1)
    evaluation_reward_summary = {
        "evaluation_episode_count": evaluation_episode_count,
        "mean_reward": mean_reward,
        "completed_task_count": completed_total,
        "dropped_task_count": dropped_total,
        "terminal_transition_count": terminal_transition_count,
        "reward_bearing_transition_count": reward_bearing_transition_count,
        "pending_at_horizon_count": pending_total,
        "trace_bank_disjoint": True,
        "trace_bank_ids": {
            "training": trainer.config.training_trace_bank_id,
            "evaluation": trainer.config.evaluation_trace_bank_id,
        },
        "trace_ids": trace_ids,
        "evaluation_on_training_traces": False,
        "same_evaluation_trace_bank": True,
    }
    evaluation_action_distribution_dict = dict(evaluation_action_distribution)
    per_action_outcome_summary_overall = {
        action: dict(bucket)
        for action, bucket in per_action_outcome_summary.items()
    }
    per_action_outcome_summary_overall["overall"] = {
        "decision_count": decision_count,
        "completed_count": completed_total,
        "dropped_count": dropped_total,
        "pending_at_horizon_count": pending_total,
        "terminal_transition_count": terminal_transition_count,
        "reward_bearing_transition_count": reward_bearing_transition_count,
        "total_reward": float(sum(rewards)),
        "mean_reward": mean_reward,
        "mean_completion_latency_slots": completion_latency_sum_total / completion_latency_count_total if completion_latency_count_total else None,
        "mean_drop_latency_slots": drop_latency_sum_total / drop_latency_count_total if drop_latency_count_total else None,
    }
    return {
        "policy_name": policy_name,
        "policy_kind": policy_kind,
        "checkpoint_budget": checkpoint_budget,
        "evaluation_episode_count": evaluation_episode_count,
        "episode_length": episode_length,
        "evaluation_trace_bank_id": evaluation_trace_bank_id or trainer.config.evaluation_trace_bank_id,
        "same_evaluation_trace_bank": True,
        "evaluation_action_distribution_source": "evaluation_episodes",
        "evaluation_action_distribution": evaluation_action_distribution_dict,
        "evaluation_decision_count": decision_count,
        "evaluation_action_sequence_sample": action_sequence_sample,
        "evaluation_legal_action_mask_distribution": dict(evaluation_legal_action_mask_distribution),
        "evaluation_action_by_trace_id": evaluation_action_by_trace_id,
        "evaluation_action_by_episode_id": evaluation_action_by_episode_id,
        "completed_count": completed_total,
        "dropped_count": dropped_total,
        "pending_at_horizon_count": pending_total,
        "mean_reward": mean_reward,
        "evaluation_reward_summary": evaluation_reward_summary,
        "per_action_outcome_summary": per_action_outcome_summary_overall,
        "reward_decomposition": reward_decomposition,
        "nan_reward_count": step_reward_nan_count,
        "zero_reward_count": step_reward_zero_count,
        "reward_available_count": reward_decomposition["reward_available_count"],
        "candidate_policy_vertical_share": evaluation_action_distribution_dict.get("vertical", 0) / max(float(decision_count), 1.0),
    }
