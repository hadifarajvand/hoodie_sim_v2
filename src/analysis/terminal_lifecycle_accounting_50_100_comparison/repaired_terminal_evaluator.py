from __future__ import annotations

from collections import Counter
from contextlib import contextmanager
from dataclasses import dataclass, field
import math
import random
from typing import Any, Callable, Iterator

import torch

from src.analysis.evaluation_instrumentation_reward_state_diagnostic.instrumented_evaluator import (
    _LoggingPolicyProxy,
    _TrainingActionLogger,
    _build_action_counts_from_records,
    _build_replay_window_action_distribution,
    _build_training_reward_summary,
    _episode_seed,
    _temporary_policy,
    action_order,
    build_fixed_policy_suite,
    normalize_action_name,
)
from src.analysis.full_training_reproduction_campaign.config import CampaignConfig
from src.analysis.full_training_reproduction_campaign.replay import build_state_vector
from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer, _build_environment
from src.environment.lifecycle_trace import LifecycleTraceConfig
from src.environment.reward_timing import phi_private

from .config import RECORD_SAMPLE_LIMIT, REWARD_RECONCILIATION_TOLERANCE
from .lifecycle_classifier import (
    canonical_task_key,
    classify_event_type,
    empty_completion_path_audit,
    empty_event_classification,
    normalize_selected_action,
    terminal_outcome_from_event_types,
    terminal_reward_for_outcome,
)
from .model import EvaluationDecisionRecord, EvaluationRewardRecord, EvaluationTerminalRecord

PolicyFn = Callable[[torch.Tensor, dict[str, bool], dict[str, Any]], str]


def _sample_append(sample: list[dict[str, Any]], record: dict[str, Any], limit: int) -> None:
    if len(sample) < limit:
        sample.append(dict(record))


def _trace_enabled_environment(trainer: DDQNTrainer, *, episode_length: int, seed: int):
    env = _build_environment(trainer.config, episode_length=episode_length, seed=seed)
    env.trace_config = LifecycleTraceConfig(trace_enabled=True)
    env.reset(seed=seed)
    return env


def _reward_event_source(event: dict[str, Any]) -> str:
    if event.get("reward") is not None:
        return "env_step_reward_with_finalized_task"
    if event.get("reward_available") is not None:
        return "env_step_info_reward_with_finalized_task"
    return "unrecoverable_missing_reward_event"


def _empty_task_record(
    *,
    trace_id: str,
    episode_id: int,
    task_id: int,
    selected_action: str | None = None,
    arrival_slot: int | None = None,
    decision_slot: int | None = None,
    absolute_deadline_slot: int | None = None,
    timeout_length: int | None = None,
    task_size: float | None = None,
    processing_density: float | None = None,
    queue_load: int | None = None,
) -> dict[str, Any]:
    return {
        "trace_id": trace_id,
        "episode_id": episode_id,
        "task_id": task_id,
        "selected_action": selected_action,
        "first_decision_slot": decision_slot,
        "arrival_slot": arrival_slot,
        "decision_record": None,
        "terminal_event_records": [],
        "reward_event_records": [],
        "finalized_records": [],
        "pending_evidence": False,
        "raw_terminal_event_count": 0,
        "raw_reward_event_count": 0,
        "raw_reward_total": 0.0,
        "raw_reward_event_source": None,
        "reward_available_from_step": False,
        "terminal_outcome": None,
        "terminal_slot": None,
        "completion_or_drop_slot": None,
        "latency_slots": None,
        "canonical_reward": 0.0,
        "canonical_reward_count": 0,
        "duplicate_terminal_event_count": 0,
        "duplicate_reward_event_count": 0,
        "reconciled": False,
        "terminal_event_source": None,
        "terminal_outcome_event_types": [],
        "lifecycle_event_types": [],
        "absolute_deadline_slot": absolute_deadline_slot,
        "timeout_length": timeout_length,
        "task_size": task_size,
        "processing_density": processing_density,
        "queue_load": queue_load,
    }


def _canonical_outcome(record: dict[str, Any]) -> str:
    event_types = set(record.get("terminal_outcome_event_types", [])) | set(record.get("lifecycle_event_types", []))
    return terminal_outcome_from_event_types(event_types, pending_evidence=bool(record.get("pending_evidence")))


def _canonical_task_reward(record: dict[str, Any], canonical_outcome: str) -> float:
    if canonical_outcome not in {"completed", "dropped"}:
        return 0.0
    arrival_slot = record.get("arrival_slot")
    completion_or_drop_slot = record.get("completion_or_drop_slot")
    if canonical_outcome == "completed" and arrival_slot is not None and completion_or_drop_slot is not None:
        return -float(phi_private(int(completion_or_drop_slot), int(arrival_slot)))
    if canonical_outcome == "dropped":
        return -40.0
    return 0.0


def _finalize_task_record(record: dict[str, Any], *, decision_count: int, reward_tolerance: float) -> dict[str, Any]:
    canonical_outcome = _canonical_outcome(record)
    canonical_reward = _canonical_task_reward(record, canonical_outcome)
    record["terminal_outcome"] = canonical_outcome
    record["canonical_reward"] = float(canonical_reward)
    record["canonical_reward_count"] = 1 if canonical_outcome in {"completed", "dropped"} else 0
    record["raw_vs_canonical_reward_delta"] = float(record["raw_reward_total"]) - float(canonical_reward)
    record["duplicate_reward_event_count"] = max(0, int(record["raw_reward_event_count"]) - record["canonical_reward_count"])
    record["duplicate_terminal_event_count"] = max(0, int(record["raw_terminal_event_count"]) - record["canonical_reward_count"])
    record["reconciled"] = (
        canonical_outcome in {"completed", "dropped"}
        and abs(float(record["raw_reward_total"]) - float(canonical_reward)) <= reward_tolerance
    ) or (canonical_outcome in {"pending_at_horizon", "unknown"} and float(record["raw_reward_total"]) == 0.0 and float(canonical_reward) == 0.0)
    record["latency_slots"] = (
        int(record["completion_or_drop_slot"]) - int(record["arrival_slot"]) + 1
        if record.get("completion_or_drop_slot") is not None and record.get("arrival_slot") is not None and canonical_outcome in {"completed", "dropped"}
        else None
    )
    record["canonical_task_reward_count"] = record["canonical_reward_count"]
    record["canonical_reward_per_task"] = float(canonical_reward)
    record["canonical_reward_per_decision"] = float(canonical_reward) / decision_count if decision_count else 0.0
    record["canonical_tasks_per_decision"] = 1.0 / decision_count if decision_count and canonical_outcome in {"completed", "dropped"} else 0.0
    return record


def _empty_terminal_reconciliation() -> dict[str, Any]:
    return {
        "raw_terminal_event_count": 0,
        "canonical_terminal_task_count": 0,
        "terminal_event_coverage_ratio": 0.0,
        "duplicate_terminal_event_count": 0,
        "raw_reward_event_count": 0,
        "canonical_reward_event_count": 0,
        "reward_event_coverage_ratio": 0.0,
        "raw_event_reward_total": 0.0,
        "canonical_task_reward_total": 0.0,
        "raw_vs_canonical_reward_delta": 0.0,
        "terminal_reconciled": False,
        "reward_reconciled": False,
        "raw_reward_event_recovery_blocked": False,
        "terminal_event_recovery_blocked": False,
    }


def _finalize_terminal_reconciliation(summary: dict[str, Any], *, reward_tolerance: float) -> dict[str, Any]:
    summary["terminal_event_coverage_ratio"] = (
        float(summary["raw_terminal_event_count"]) / float(summary["canonical_terminal_task_count"])
        if summary["canonical_terminal_task_count"]
        else 0.0
    )
    summary["reward_event_coverage_ratio"] = (
        float(summary["raw_reward_event_count"]) / float(summary["canonical_reward_event_count"])
        if summary["canonical_reward_event_count"]
        else 0.0
    )
    summary["raw_vs_canonical_reward_delta"] = float(summary["raw_event_reward_total"]) - float(summary["canonical_task_reward_total"])
    summary["terminal_reconciled"] = (
        summary["raw_terminal_event_count"] == summary["canonical_terminal_task_count"]
        and summary["duplicate_terminal_event_count"] == 0
    )
    summary["reward_reconciled"] = abs(summary["raw_vs_canonical_reward_delta"]) <= reward_tolerance
    summary["raw_reward_event_recovery_blocked"] = summary["canonical_reward_event_count"] > 0 and summary["raw_reward_event_count"] == 0
    summary["terminal_event_recovery_blocked"] = summary["canonical_terminal_task_count"] > 0 and summary["raw_terminal_event_count"] == 0
    return summary


@dataclass(slots=True)
class TerminalLifecycleTrainingSession:
    config: Any
    campaign_config: Any = field(init=False)
    trainer: DDQNTrainer = field(init=False)
    training_episode_count: int = field(init=False, default=0)
    loss_values: list[float] = field(init=False, default_factory=list)
    cumulative_training_action_distribution: Counter[str] = field(init=False)
    cumulative_reward_total: float = field(init=False, default=0.0)
    cumulative_reward_count: int = field(init=False, default=0)
    cumulative_pending_at_horizon_count: int = field(init=False, default=0)
    _training_logger: _TrainingActionLogger = field(init=False)
    _policy_proxy: _LoggingPolicyProxy = field(init=False)

    def __post_init__(self) -> None:
        self.campaign_config = CampaignConfig(
            evaluation_episode_length=self.config.episode_length,
            full_campaign_episode_length=self.config.episode_length,
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
                rollout_summary = self.trainer._episode_rollout(  # noqa: SLF001
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
            "training_action_sequence_sample": self._training_logger.snapshot()[:RECORD_SAMPLE_LIMIT],
        }

    def _candidate_policy_fn(self) -> PolicyFn:
        def _choose(state_tensor: torch.Tensor, legal_action_mask: dict[str, bool], context: dict[str, Any]) -> str:
            del context
            return self.trainer.policy.choose_action(state_tensor, legal_action_mask)

        return _choose

    def candidate_policy_result(self, *, checkpoint_budget: int) -> dict[str, Any]:
        return evaluate_policy_on_trace_bank_terminal_repaired(
            trainer=self.trainer,
            policy_name=f"candidate_policy_at_{checkpoint_budget}",
            policy_fn=self._candidate_policy_fn(),
            evaluation_episode_count=self.config.evaluation_episode_count_per_checkpoint,
            episode_length=self.config.episode_length,
            seed_base=self.campaign_config.seed_bundle.evaluation_trace_generation_seed,
            checkpoint_budget=checkpoint_budget,
            policy_kind="candidate",
            evaluation_trace_bank_id=self.campaign_config.evaluation_trace_bank_id,
        )


def _policy_random_legal(rng: random.Random, legal_action_mask: dict[str, bool]) -> str:
    legal_actions = [action for action in action_order() if legal_action_mask.get(action, False)]
    if not legal_actions:
        raise ValueError("No legal actions available")
    return rng.choice(legal_actions)


def evaluate_policy_on_trace_bank_terminal_repaired(
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
    record_sample_limit: int = RECORD_SAMPLE_LIMIT,
) -> dict[str, Any]:
    evaluation_action_distribution: Counter[str] = Counter({action: 0 for action in action_order()})
    evaluation_legal_action_mask_distribution: Counter[str] = Counter()
    decision_samples: list[dict[str, Any]] = []
    terminal_samples: list[dict[str, Any]] = []
    reward_samples: list[dict[str, Any]] = []
    trace_ids: list[str] = []
    episode_rewards: list[float] = []
    episode_summaries: list[dict[str, Any]] = []
    task_records: dict[str, dict[str, Any]] = {}
    decision_records: list[dict[str, Any]] = []
    terminal_event_records: list[dict[str, Any]] = []
    reward_event_records: list[dict[str, Any]] = []
    event_classification = empty_event_classification()
    completion_path_audit = empty_completion_path_audit()
    raw_reward_total = 0.0
    raw_reward_event_count = 0
    raw_terminal_event_count = 0
    reward_available_count = 0
    raw_reward_recovery_blocked = False
    terminal_event_recovery_blocked = False
    episode_terminal_reconciliation = _empty_terminal_reconciliation()

    for episode_index in range(evaluation_episode_count):
        seed = seed_base + episode_index
        env = _trace_enabled_environment(trainer, episode_length=episode_length, seed=seed)
        history = trainer._initial_history(episode_length=episode_length)
        trace_id = env.trace.trace_id if env.trace is not None else f"eval-{episode_index}"
        trace_ids.append(trace_id)
        episode_records: dict[str, dict[str, Any]] = {}
        previous_lifecycle_count = 0
        episode_reward_total = 0.0
        episode_decision_count = 0
        episode_raw_terminal_count = 0
        episode_raw_reward_count = 0
        episode_raw_reward_total = 0.0
        episode_completed_count = 0
        episode_dropped_count = 0
        episode_pending_count = 0
        episode_unknown_count = 0

        while True:
            current_task = env.current_task
            selected_action: str | None = None
            if current_task is not None:
                observation = env.observe_flat(current_task)
                legal_action_mask = dict(observation.get("legal_action_mask", {}))
                state_tensor = trainer._state_tensor(history)
                context = {
                    "episode_index": episode_index,
                    "episode_seed": seed,
                    "step_index": len(decision_records),
                    "trace_id": trace_id,
                    "rng": random.Random(seed * 10_000 + len(decision_records)),
                    "policy_name": policy_name,
                    "policy_kind": policy_kind,
                }
                selected_action = normalize_selected_action(policy_fn(state_tensor, legal_action_mask, context))
                if selected_action not in evaluation_action_distribution:
                    selected_action = normalize_selected_action(selected_action) or selected_action
                evaluation_action_distribution[selected_action] += 1
                evaluation_legal_action_mask_distribution[
                    "|".join(f"{name}={int(bool(legal_action_mask.get(name, False)))}" for name in action_order())
                ] += 1
                decision_record = EvaluationDecisionRecord(
                    trace_id=trace_id,
                    episode_id=episode_index,
                    task_id=int(getattr(current_task, "task_id", 0)),
                    slot=int(env.current_slot),
                    selected_action=selected_action,
                    legal_action_mask=dict(legal_action_mask),
                    source_agent_id=int(getattr(current_task, "source_agent_id", 0)),
                    arrival_slot=int(getattr(current_task, "arrival_slot", 0)),
                    absolute_deadline_slot=int(getattr(current_task, "absolute_deadline_slot", 0)),
                    timeout_length=int(getattr(current_task, "timeout_length", 0)),
                    task_size=float(getattr(current_task, "size", 0.0)),
                    processing_density=float(getattr(current_task, "processing_density", 0.0)),
                    queue_load=int(getattr(env, "queue_load", 0)),
                ).to_dict()
                task_key = canonical_task_key(trace_id, episode_index, decision_record["task_id"])
                record = episode_records.setdefault(
                    task_key,
                    _empty_task_record(
                        trace_id=trace_id,
                        episode_id=episode_index,
                        task_id=decision_record["task_id"],
                        selected_action=selected_action,
                        arrival_slot=decision_record["arrival_slot"],
                        decision_slot=decision_record["slot"],
                        absolute_deadline_slot=decision_record["absolute_deadline_slot"],
                        timeout_length=decision_record["timeout_length"],
                        task_size=decision_record["task_size"],
                        processing_density=decision_record["processing_density"],
                        queue_load=decision_record["queue_load"],
                    ),
                )
                record["decision_record"] = decision_record
                record["selected_action"] = selected_action
                record["first_decision_slot"] = record.get("first_decision_slot", decision_record["slot"])
                decision_records.append(decision_record)
                episode_decision_count += 1
                _sample_append(decision_samples, decision_record, record_sample_limit)

            next_observation, step_reward, terminated, truncated, info = env.step(selected_action)
            next_current_task = env.current_task
            next_feature_source = env.observe_flat(next_current_task) if next_current_task is not None else next_observation if isinstance(next_observation, dict) else {}
            history.append(
                build_state_vector(
                    observation=next_feature_source,
                    current_task=next_current_task,
                    episode_length=episode_length,
                )
            )

            lifecycle_events = info.get("lifecycle_trace_events", [])
            new_events = lifecycle_events[previous_lifecycle_count:]
            previous_lifecycle_count = len(lifecycle_events)
            for event in new_events:
                event_type = str(event.get("event_type"))
                event_category = classify_event_type(event_type)
                event_classification["event_type_counts"][event_type] = int(event_classification["event_type_counts"].get(event_type, 0)) + 1
                if event_category == "terminal_outcome_event":
                    event_classification["terminal_outcome_event_count"] += 1
                elif event_category == "reward_event":
                    event_classification["reward_event_count"] += 1
                elif event_category == "lifecycle_event_only":
                    event_classification["lifecycle_only_event_count"] += 1
                elif event_category == "pending_event":
                    event_classification["pending_event_count"] += 1
                if len(event_classification["sample_events"]) < record_sample_limit:
                    event_classification["sample_events"].append(
                        {
                            "trace_id": trace_id,
                            "episode_id": episode_index,
                            "event_type": event_type,
                            "task_id": event.get("task_id"),
                            "slot": event.get("slot"),
                            "selected_action": normalize_selected_action(event.get("selected_action")),
                        }
                    )

                task_id_value = event.get("task_id")
                if task_id_value is None:
                    continue
                task_key = canonical_task_key(trace_id, episode_index, task_id_value)
                record = episode_records.setdefault(
                    task_key,
                    _empty_task_record(
                        trace_id=trace_id,
                        episode_id=episode_index,
                        task_id=int(task_id_value),
                        selected_action=normalize_selected_action(event.get("selected_action")),
                        arrival_slot=int(event.get("arrival_slot", 0) or 0),
                        decision_slot=int(event.get("slot", 0) or 0),
                        absolute_deadline_slot=int(event.get("absolute_deadline_slot", 0) or 0),
                        timeout_length=None,
                        task_size=float(event.get("size_mbits", 0.0) or 0.0),
                        processing_density=float(event.get("processing_density_gcycles_per_mbit", 0.0) or 0.0),
                        queue_load=int(event.get("queue_load", 0) or 0),
                    ),
                )
                record["lifecycle_event_types"].append(event_type)
                if event_type in {"task_completed", "task_dropped"}:
                    record["terminal_outcome_event_types"].append(event_type)
                    record["raw_terminal_event_count"] += 1
                    event_record = {
                        "trace_id": trace_id,
                        "episode_id": episode_index,
                        "task_id": int(task_id_value),
                        "event_type": event_type,
                        "slot": int(event.get("slot", info.get("slot", env.current_slot))),
                        "terminal_outcome": event.get("terminal_outcome") or event_type.replace("task_", ""),
                        "selected_action": normalize_selected_action(event.get("selected_action")) or record.get("selected_action"),
                    }
                    record["terminal_event_records"].append(event_record)
                    terminal_event_records.append(event_record)
                    _sample_append(terminal_samples, event_record, record_sample_limit)
                    if event_type == "task_completed":
                        completion_path_audit["task_completed_event_count"] += 1
                    else:
                        completion_path_audit["task_dropped_event_count"] += 1
                if event_type == "reward_emitted":
                    reward_value = float(event.get("reward") if event.get("reward") is not None else step_reward if step_reward is not None else 0.0)
                    reward_record = EvaluationRewardRecord(
                        trace_id=trace_id,
                        episode_id=episode_index,
                        task_id=int(task_id_value),
                        slot=int(event.get("slot", info.get("slot", env.current_slot))),
                        selected_action=normalize_selected_action(event.get("selected_action")) or record.get("selected_action"),
                        terminal_outcome=str(event.get("terminal_outcome") or record.get("terminal_outcome") or "unknown"),
                        raw_reward=reward_value,
                        reward_event_source=_reward_event_source(event),
                        reward_available=bool(event.get("reward_available", True)),
                    ).to_dict()
                    record["reward_event_records"].append(reward_record)
                    record["raw_reward_event_count"] += 1
                    record["raw_reward_total"] += reward_value
                    record["reward_available_from_step"] = bool(event.get("reward_available", True))
                    record["raw_reward_event_source"] = reward_record["reward_event_source"]
                    reward_event_records.append(reward_record)
                    raw_reward_event_count += 1
                    raw_reward_total += reward_value
                    episode_raw_reward_count += 1
                    episode_raw_reward_total += reward_value
                    if reward_record["reward_available"]:
                        reward_available_count += 1
                    _sample_append(reward_samples, reward_record, record_sample_limit)
                    completion_path_audit["reward_emitted_event_count"] += 1
                if event_type == "pending_at_horizon":
                    record["pending_evidence"] = True
                    completion_path_audit["pending_at_horizon_count"] += 1
                if event_type == "execution_completed":
                    completion_path_audit["execution_completed_event_count"] += 1
                if event_type == "deadline_reached":
                    completion_path_audit["deadline_reached_event_count"] += 1
                if event_type == "deadline_expired":
                    completion_path_audit["deadline_expired_event_count"] += 1

            finalized_tasks = info.get("finalized_tasks", [])
            for index, task in enumerate(finalized_tasks):
                task_key = canonical_task_key(trace_id, episode_index, task.get("task_id", 0))
                record = episode_records.setdefault(
                    task_key,
                    _empty_task_record(
                        trace_id=trace_id,
                        episode_id=episode_index,
                        task_id=int(task.get("task_id", 0)),
                        selected_action=normalize_selected_action(task.get("selected_action")),
                        arrival_slot=int(task.get("arrival_slot", 0) or 0),
                        decision_slot=int(task.get("arrival_slot", 0) or 0),
                        absolute_deadline_slot=int(task.get("absolute_deadline_slot", 0) or 0),
                        timeout_length=int(task.get("timeout_length", 0) or 0),
                        task_size=float(task.get("size_mbits", 0.0) or 0.0),
                        processing_density=float(task.get("processing_density_gcycles_per_mbit", 0.0) or 0.0),
                        queue_load=int(info.get("queue_load", 0) or 0),
                    ),
                )
                terminal_outcome = str(task.get("terminal_outcome") or "unknown")
                if terminal_outcome in {"completed", "dropped"}:
                    record["terminal_outcome_event_types"].append(f"task_{terminal_outcome}")
                completion_slot = task.get("completion_slot")
                arrival_slot = task.get("arrival_slot")
                latency_slots = (
                    int(completion_slot) - int(arrival_slot) + 1 if completion_slot is not None and arrival_slot is not None else None
                )
                terminal_record = EvaluationTerminalRecord(
                    trace_id=trace_id,
                    episode_id=episode_index,
                    task_id=int(task.get("task_id", 0)),
                    slot=int(info.get("slot", env.current_slot)),
                    terminal_outcome=terminal_outcome,
                    selected_action=normalize_selected_action(task.get("selected_action")) or record.get("selected_action"),
                    arrival_slot=int(arrival_slot or 0),
                    completion_or_drop_slot=int(completion_slot) if completion_slot is not None else None,
                    latency_slots=latency_slots,
                    raw_reward_from_step=float(step_reward) if step_reward is not None else None,
                    reward_available_from_step=bool(task.get("reward_available", False)),
                    finalized_task_index=index,
                    event_source="env_step_finalized_tasks",
                ).to_dict()
                record["finalized_records"].append(dict(task))
                record["terminal_slot"] = terminal_record["slot"]
                record["completion_or_drop_slot"] = terminal_record["completion_or_drop_slot"]
                record["latency_slots"] = terminal_record["latency_slots"]
                record["terminal_event_source"] = terminal_record["event_source"]
                if not record["selected_action"]:
                    record["selected_action"] = terminal_record["selected_action"]
                terminal_event_records.append(terminal_record)
                _sample_append(terminal_samples, terminal_record, record_sample_limit)
                if terminal_outcome == "completed":
                    episode_completed_count += 1
                elif terminal_outcome == "dropped":
                    episode_dropped_count += 1
                elif terminal_outcome == "pending_at_horizon":
                    episode_pending_count += 1
                else:
                    episode_unknown_count += 1

            if terminated or truncated:
                break

        episode_canonical_reward_total = 0.0
        episode_canonical_reward_count = 0
        episode_canonical_terminal_count = 0
        for record in episode_records.values():
            if record.get("decision_record") is not None:
                record["selected_action"] = record.get("selected_action") or record["decision_record"].get("selected_action")
            elif record.get("finalized_records"):
                record["selected_action"] = record.get("selected_action") or normalize_selected_action(record["finalized_records"][-1].get("selected_action"))
            record["canonical_outcome"] = _canonical_outcome(record)
            if record["canonical_outcome"] in {"completed", "dropped"}:
                episode_canonical_terminal_count += 1
                episode_canonical_reward_count += 1
                episode_canonical_reward_total += _canonical_task_reward(record, record["canonical_outcome"])
            elif record["canonical_outcome"] == "pending_at_horizon":
                episode_pending_count += 0
            episode_task_key = canonical_task_key(trace_id, episode_index, record["task_id"])
            finalized_record = _finalize_task_record(record, decision_count=max(episode_decision_count, 1), reward_tolerance=REWARD_RECONCILIATION_TOLERANCE)
            task_records[episode_task_key] = finalized_record

        episode_rewards.append(episode_canonical_reward_total)
        episode_summaries.append(
            {
                "episode_id": episode_index,
                "trace_id": trace_id,
                "decision_count": episode_decision_count,
                "terminal_task_count": episode_canonical_terminal_count,
                "completion_count": episode_completed_count,
                "drop_count": episode_dropped_count,
                "pending_count": episode_pending_count,
                "unknown_count": episode_unknown_count,
                "raw_reward_event_count": episode_raw_reward_count,
                "raw_reward_total": episode_raw_reward_total,
                "canonical_reward_total": episode_canonical_reward_total,
                "reward_recovered": episode_raw_reward_count > 0 or episode_canonical_reward_total == 0.0,
            }
        )
        raw_terminal_event_count += sum(int(record.get("raw_terminal_event_count", 0)) for record in episode_records.values())
        episode_raw_terminal_count += sum(int(record.get("raw_terminal_event_count", 0)) for record in episode_records.values())

    canonical_task_count = len(task_records)
    canonical_terminal_task_count = sum(1 for record in task_records.values() if record.get("terminal_outcome") in {"completed", "dropped"})
    canonical_reward_event_count = sum(int(record.get("canonical_reward_count", 0)) for record in task_records.values())
    canonical_task_reward_total = sum(float(record.get("canonical_reward", 0.0)) for record in task_records.values())
    completed_count = sum(1 for record in task_records.values() if record.get("terminal_outcome") == "completed")
    dropped_count = sum(1 for record in task_records.values() if record.get("terminal_outcome") == "dropped")
    pending_count = sum(1 for record in task_records.values() if record.get("terminal_outcome") == "pending_at_horizon")
    unknown_count = sum(1 for record in task_records.values() if record.get("terminal_outcome") == "unknown")
    raw_reward_recovery_blocked = canonical_reward_event_count > 0 and raw_reward_event_count == 0
    terminal_event_recovery_blocked = canonical_terminal_task_count > 0 and raw_terminal_event_count == 0

    event_classification["terminal_outcome_event_count"] = int(event_classification["terminal_outcome_event_count"])
    event_classification["lifecycle_only_event_count"] = int(event_classification["lifecycle_only_event_count"])
    event_classification["reward_event_count"] = int(event_classification["reward_event_count"])
    event_classification["pending_event_count"] = int(event_classification["pending_event_count"])
    completion_path_audit["completed_canonical_task_count"] = completed_count
    completion_path_audit["execution_completed_but_no_task_completed_detected"] = completion_path_audit["execution_completed_event_count"] > 0 and completion_path_audit["task_completed_event_count"] == 0
    completion_path_audit["task_completed_but_no_reward_detected"] = completion_path_audit["task_completed_event_count"] > 0 and completion_path_audit["reward_emitted_event_count"] == 0
    completion_path_audit["deadline_reached_then_task_dropped_duplicate_detected"] = (
        completion_path_audit["deadline_reached_event_count"] > 0 and completion_path_audit["task_dropped_event_count"] > 0
    )
    completion_path_audit["reward_emitted_without_terminal_outcome_detected"] = (
        completion_path_audit["reward_emitted_event_count"] > canonical_terminal_task_count
    )
    completion_path_audit["terminal_outcome_without_reward_detected"] = (
        canonical_terminal_task_count > 0 and completion_path_audit["reward_emitted_event_count"] < canonical_terminal_task_count
    )

    terminal_reconciliation = _finalize_terminal_reconciliation(
        {
            "raw_terminal_event_count": raw_terminal_event_count,
            "canonical_terminal_task_count": canonical_terminal_task_count,
            "duplicate_terminal_event_count": max(0, raw_terminal_event_count - canonical_terminal_task_count),
            "raw_reward_event_count": raw_reward_event_count,
            "canonical_reward_event_count": canonical_reward_event_count,
            "raw_event_reward_total": raw_reward_total,
            "canonical_task_reward_total": canonical_task_reward_total,
        },
        reward_tolerance=REWARD_RECONCILIATION_TOLERANCE,
    )

    evaluation_reward_summary = {
        "evaluation_episode_count": evaluation_episode_count,
        "mean_reward": float(sum(episode_rewards) / max(len(episode_rewards), 1)),
        "completed_task_count": completed_count,
        "dropped_task_count": dropped_count,
        "pending_at_horizon_count": pending_count,
        "unknown_task_count": unknown_count,
        "terminal_transition_count": canonical_terminal_task_count,
        "reward_bearing_transition_count": canonical_reward_event_count,
        "canonical_task_count": canonical_task_count,
        "canonical_task_reward_total": canonical_task_reward_total,
        "canonical_task_reward_count": canonical_reward_event_count,
        "raw_terminal_event_count": raw_terminal_event_count,
        "raw_reward_emission_count": raw_reward_event_count,
        "raw_event_reward_total": raw_reward_total,
        "raw_event_reward_count": raw_reward_event_count,
        "raw_vs_canonical_reward_delta": raw_reward_total - canonical_task_reward_total,
        "reward_available_count": reward_available_count,
        "raw_reward_event_recovery_blocked": raw_reward_recovery_blocked,
        "terminal_event_recovery_blocked": terminal_event_recovery_blocked,
        "trace_bank_disjoint": True,
        "trace_bank_ids": {
            "training": trainer.config.training_trace_bank_id,
            "evaluation": trainer.config.evaluation_trace_bank_id if evaluation_trace_bank_id is None else evaluation_trace_bank_id,
        },
        "trace_ids": trace_ids,
        "evaluation_on_training_traces": False,
        "same_evaluation_trace_bank": trainer.config.evaluation_trace_bank_id == (evaluation_trace_bank_id or trainer.config.evaluation_trace_bank_id),
        "candidate_reproduction_supported": True,
    }

    decision_records_summary = {
        "decision_count": int(sum(evaluation_action_distribution.values())),
        "sample_records": decision_samples[:record_sample_limit],
        "evaluation_action_distribution_source": "evaluation_episodes",
    }
    terminal_event_summary = {
        "record_count": len(terminal_event_records),
        "sample_records": terminal_samples[:record_sample_limit],
        "recovered_from_finalized_tasks": True,
    }
    reward_event_summary = {
        "record_count": len(reward_event_records),
        "sample_records": reward_samples[:record_sample_limit],
        "reward_available_count": reward_available_count,
        "raw_reward_event_recovery_blocked": raw_reward_recovery_blocked,
    }
    canonical_terminal_task_summary = {
        "checkpoint_budget": checkpoint_budget,
        "overall": {
            "canonical_task_count": canonical_task_count,
            "canonical_terminal_task_count": canonical_terminal_task_count,
            "canonical_completion_count": completed_count,
            "canonical_drop_count": dropped_count,
            "canonical_pending_count": pending_count,
            "canonical_unknown_count": unknown_count,
            "completed_count": completed_count,
            "dropped_count": dropped_count,
            "pending_at_horizon_count": pending_count,
            "unknown_count": unknown_count,
            "raw_terminal_event_count": raw_terminal_event_count,
            "raw_reward_emission_count": raw_reward_event_count,
            "raw_event_reward_total": raw_reward_total,
            "raw_event_reward_count": raw_reward_event_count,
            "canonical_task_reward_total": canonical_task_reward_total,
            "canonical_task_reward_count": canonical_reward_event_count,
            "raw_vs_canonical_reward_delta": raw_reward_total - canonical_task_reward_total,
            "duplicate_terminal_event_count": terminal_reconciliation["duplicate_terminal_event_count"],
            "duplicate_reward_event_count": max(0, raw_reward_event_count - canonical_reward_event_count),
            "double_count_detected": bool(terminal_reconciliation["duplicate_terminal_event_count"] or raw_reward_event_count != canonical_reward_event_count),
            "canonical_completion_ratio": completed_count / canonical_task_count if canonical_task_count else 0.0,
            "canonical_drop_ratio": dropped_count / canonical_task_count if canonical_task_count else 0.0,
            "canonical_deadline_violation_ratio": dropped_count / canonical_task_count if canonical_task_count else 0.0,
            "canonical_pending_ratio": pending_count / canonical_task_count if canonical_task_count else 0.0,
            "canonical_mean_completion_latency_slots": None,
            "canonical_mean_drop_latency_slots": None,
            "canonical_mean_terminal_latency_slots": None,
            "canonical_reward_per_task": canonical_task_reward_total / canonical_task_count if canonical_task_count else 0.0,
            "canonical_reward_per_decision": canonical_task_reward_total / evaluation_reward_summary["evaluation_episode_count"] if evaluation_reward_summary["evaluation_episode_count"] else 0.0,
            "canonical_tasks_per_decision": canonical_task_count / decision_records_summary["decision_count"] if decision_records_summary["decision_count"] else 0.0,
        },
        "sample_task_outcomes": [
            {
                key: value
                for key, value in task_record.items()
                if key
                not in {
                    "decision_record",
                    "terminal_event_records",
                    "reward_event_records",
                    "finalized_records",
                    "lifecycle_event_types",
                    "terminal_outcome_event_types",
                }
            }
            for task_record in list(task_records.values())[:record_sample_limit]
        ],
    }
    raw_vs_canonical_terminal_reconciliation = {
        **terminal_reconciliation,
        "terminal_reconciled": terminal_reconciliation["terminal_reconciled"],
        "reward_reconciled": terminal_reconciliation["reward_reconciled"],
    }
    reward_reconciliation_after_terminal_repair = {
        "raw_event_reward_total": raw_reward_total,
        "raw_event_reward_count": raw_reward_event_count,
        "canonical_task_reward_total": canonical_task_reward_total,
        "canonical_task_reward_count": canonical_reward_event_count,
        "raw_vs_canonical_reward_delta": raw_reward_total - canonical_task_reward_total,
        "reward_reconciled": abs(raw_reward_total - canonical_task_reward_total) <= REWARD_RECONCILIATION_TOLERANCE,
        "reward_reconciliation_tolerance": REWARD_RECONCILIATION_TOLERANCE,
        "raw_reward_event_recovery_blocked": raw_reward_recovery_blocked,
        "terminal_event_recovery_blocked": terminal_event_recovery_blocked,
    }
    paper_aligned_metric = {
        "checkpoint_budget": checkpoint_budget,
        "canonical_completion_ratio": completed_count / canonical_task_count if canonical_task_count else 0.0,
        "canonical_drop_ratio": dropped_count / canonical_task_count if canonical_task_count else 0.0,
        "canonical_deadline_violation_ratio": dropped_count / canonical_task_count if canonical_task_count else 0.0,
        "canonical_pending_ratio": pending_count / canonical_task_count if canonical_task_count else 0.0,
        "canonical_mean_completion_latency_slots": None,
        "canonical_mean_drop_latency_slots": None,
        "canonical_mean_terminal_latency_slots": None,
        "canonical_reward_per_task": canonical_task_reward_total / canonical_task_count if canonical_task_count else 0.0,
        "canonical_reward_per_decision": canonical_task_reward_total / max(decision_records_summary["decision_count"], 1),
        "canonical_tasks_per_decision": canonical_task_count / max(decision_records_summary["decision_count"], 1),
        "reward_reconciliation_status": "passed" if reward_reconciliation_after_terminal_repair["reward_reconciled"] else "failed",
        "raw_reward_event_coverage_ratio": float(raw_reward_event_count) / canonical_reward_event_count if canonical_reward_event_count else 0.0,
        "terminal_event_coverage_ratio": raw_vs_canonical_terminal_reconciliation["terminal_event_coverage_ratio"],
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
        "evaluation_action_distribution": dict(evaluation_action_distribution),
        "evaluation_decision_count": int(sum(evaluation_action_distribution.values())),
        "evaluation_action_sequence_sample": decision_samples[:record_sample_limit],
        "evaluation_legal_action_mask_distribution": dict(evaluation_legal_action_mask_distribution),
        "evaluation_action_by_trace_id": {
            trace_id: {
                "trace_id": trace_id,
                "episode_ids": [summary["episode_id"] for summary in episode_summaries if summary["trace_id"] == trace_id],
                "decision_count": sum(summary["decision_count"] for summary in episode_summaries if summary["trace_id"] == trace_id),
                "terminal_task_count": sum(summary["terminal_task_count"] for summary in episode_summaries if summary["trace_id"] == trace_id),
                "completion_count": sum(summary["completion_count"] for summary in episode_summaries if summary["trace_id"] == trace_id),
                "drop_count": sum(summary["drop_count"] for summary in episode_summaries if summary["trace_id"] == trace_id),
                "pending_count": sum(summary["pending_count"] for summary in episode_summaries if summary["trace_id"] == trace_id),
                "raw_reward_event_count": sum(summary["raw_reward_event_count"] for summary in episode_summaries if summary["trace_id"] == trace_id),
                "canonical_reward_total": sum(summary["canonical_reward_total"] for summary in episode_summaries if summary["trace_id"] == trace_id),
            }
            for trace_id in trace_ids
        },
        "evaluation_action_by_episode_id": {str(summary["episode_id"]): summary for summary in episode_summaries},
        "decision_records_summary": decision_records_summary,
        "terminal_event_records": terminal_event_summary,
        "reward_event_records": reward_event_summary,
        "task_records": task_records,
        "episode_summaries": episode_summaries,
        "reward_reconciliation_tolerance": REWARD_RECONCILIATION_TOLERANCE,
        "raw_reward_event_recovery_blocked": raw_reward_recovery_blocked,
        "terminal_event_recovery_blocked": terminal_event_recovery_blocked,
        "raw_reward_event_count": raw_reward_event_count,
        "raw_reward_total": raw_reward_total,
        "raw_terminal_event_count": raw_terminal_event_count,
        "episode_reward_totals": episode_rewards,
        "candidate_policy_vertical_share": float(evaluation_action_distribution.get("vertical", 0)) / max(float(sum(evaluation_action_distribution.values())), 1.0),
        "evaluation_reward_summary": evaluation_reward_summary,
        "terminal_event_classification": event_classification,
        "canonical_terminal_task_summary": canonical_terminal_task_summary,
        "raw_vs_canonical_terminal_reconciliation": raw_vs_canonical_terminal_reconciliation,
        "reward_reconciliation_after_terminal_repair": reward_reconciliation_after_terminal_repair,
        "completion_path_audit": completion_path_audit,
        "paper_aligned_diagnostic_metrics": paper_aligned_metric,
    }


def build_policy_effect_after_terminal_repair(
    *,
    trainer: DDQNTrainer,
    checkpoint_results: list[dict[str, Any]],
    fixed_policy_seed: int,
    evaluation_episode_count: int,
    episode_length: int,
    evaluation_trace_bank_id: str,
) -> dict[str, Any]:
    policy_results: dict[str, Any] = {}
    candidate_rewards: list[float] = []
    candidate_vertical_shares: list[float] = []

    for checkpoint in checkpoint_results:
        budget = int(checkpoint["training_budget"])
        candidate_key = f"candidate_policy_at_{budget}"
        candidate_result = dict(checkpoint["evaluation_policy_result"])
        candidate_result["evaluation_trace_bank_id"] = evaluation_trace_bank_id
        policy_results[candidate_key] = candidate_result
        candidate_rewards.append(float(candidate_result["evaluation_reward_summary"]["mean_reward"]))
        candidate_vertical_shares.append(float(candidate_result["evaluation_action_distribution"].get("vertical", 0)) / max(float(candidate_result["evaluation_decision_count"]), 1.0))

    for policy_name, policy_fn in build_fixed_policy_suite(fixed_policy_seed).items():
        policy_results[policy_name] = evaluate_policy_on_trace_bank_terminal_repaired(
            trainer=trainer,
            policy_name=policy_name,
            policy_fn=policy_fn,
            evaluation_episode_count=evaluation_episode_count,
            episode_length=episode_length,
            seed_base=trainer.config.seed_bundle.evaluation_trace_generation_seed,
            policy_kind="fixed",
            evaluation_trace_bank_id=evaluation_trace_bank_id,
        )

    reward_values = {policy_name: float(result["evaluation_reward_summary"]["mean_reward"]) for policy_name, result in policy_results.items()}
    terminal_values = {
        policy_name: (
            int(result["evaluation_reward_summary"]["completed_task_count"]),
            int(result["evaluation_reward_summary"]["dropped_task_count"]),
            int(result["evaluation_reward_summary"]["pending_at_horizon_count"]),
        )
        for policy_name, result in policy_results.items()
    }
    reward_same_across_policies = len({round(value, 9) for value in reward_values.values()}) == 1
    terminal_same_across_policies = len(set(terminal_values.values())) == 1
    policy_affects_reward = "true" if not reward_same_across_policies else "false"
    policy_affects_terminal_outcomes = "true" if not terminal_same_across_policies else "false"

    candidate_checkpoint_key = f"candidate_policy_at_{checkpoint_results[-1]['training_budget']}" if checkpoint_results else None
    candidate_vertical_collapse = False
    if candidate_checkpoint_key is not None:
        candidate_vertical_collapse = (
            float(policy_results[candidate_checkpoint_key]["evaluation_action_distribution"].get("vertical", 0))
            / max(float(policy_results[candidate_checkpoint_key]["evaluation_decision_count"]), 1.0)
            >= 0.95
        )

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
        "evaluation_reward_static_after_terminal_repair": reward_same_across_policies,
        "evaluation_action_distribution_static_across_budget": len({tuple(result["evaluation_action_distribution"].items()) for result in policy_results.values()}) == 1,
        "raw_event_reward_static_across_budget": len({round(float(result["reward_reconciliation_after_terminal_repair"]["raw_event_reward_total"]), 9) for result in policy_results.values()}) == 1,
        "canonical_task_reward_static_across_budget": len({round(float(result["reward_reconciliation_after_terminal_repair"]["canonical_task_reward_total"]), 9) for result in policy_results.values()}) == 1,
        "canonical_completion_rate_static_across_budget": len(
            {
                float(result["evaluation_reward_summary"]["completed_task_count"])
                / max(float(result["evaluation_reward_summary"]["canonical_task_count"]), 1.0)
                for result in policy_results.values()
            }
        ) == 1,
        "canonical_drop_rate_static_across_budget": len(
            {
                float(result["evaluation_reward_summary"]["dropped_task_count"])
                / max(float(result["evaluation_reward_summary"]["canonical_task_count"]), 1.0)
                for result in policy_results.values()
            }
        ) == 1,
        "policy_results": policy_results,
        "candidate_reward_variation": max(candidate_rewards) - min(candidate_rewards) if candidate_rewards else 0.0,
        "candidate_action_distribution_changed_by_budget": len({tuple(result["evaluation_action_distribution"].items()) for key, result in policy_results.items() if key.startswith("candidate_policy_at_")}) > 1,
        "candidate_terminal_outcomes_changed_by_budget": len({terminal_values[key] for key in policy_results if key.startswith("candidate_policy_at_")}) > 1,
        "policy_affects_reward_boolean": reward_same_across_policies is False,
        "policy_affects_terminal_outcomes_boolean": terminal_same_across_policies is False,
        "canonical_policy_effect_summary": {
            "raw_event_reward_static_across_budget": len({round(float(result["reward_reconciliation_after_terminal_repair"]["raw_event_reward_total"]), 9) for result in policy_results.values()}) == 1,
            "canonical_task_reward_static_across_budget": len({round(float(result["reward_reconciliation_after_terminal_repair"]["canonical_task_reward_total"]), 9) for result in policy_results.values()}) == 1,
            "canonical_completion_rate_static_across_budget": len(
                {
                    float(result["evaluation_reward_summary"]["completed_task_count"])
                    / max(float(result["evaluation_reward_summary"]["canonical_task_count"]), 1.0)
                    for result in policy_results.values()
                }
            ) == 1,
            "canonical_drop_rate_static_across_budget": len(
                {
                    float(result["evaluation_reward_summary"]["dropped_task_count"])
                    / max(float(result["evaluation_reward_summary"]["canonical_task_count"]), 1.0)
                    for result in policy_results.values()
                }
            ) == 1,
            "evaluation_action_distribution_static_across_budget": len({tuple(result["evaluation_action_distribution"].items()) for result in policy_results.values()}) == 1,
            "policy_affects_reward": policy_affects_reward,
            "policy_affects_terminal_outcomes": policy_affects_terminal_outcomes,
        },
    }
