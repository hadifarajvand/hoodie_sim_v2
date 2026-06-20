from __future__ import annotations

from collections import Counter
import random
from typing import Any, Callable

import torch

from src.analysis.evaluation_instrumentation_reward_state_diagnostic.instrumented_evaluator import (
    action_order,
    build_fixed_policy_suite,
    normalize_action_name,
)
from src.analysis.full_training_reproduction_campaign.replay import build_state_vector
from src.analysis.full_training_reproduction_campaign.trainer import _build_environment
from src.environment.lifecycle_trace import LifecycleTraceConfig
from src.environment.reward_timing import phi_private

from .config import RECORD_SAMPLE_LIMIT, REWARD_RECONCILIATION_TOLERANCE
from .model import EvaluationDecisionRecord, EvaluationRewardRecord, EvaluationTerminalRecord

PolicyFn = Callable[[torch.Tensor, dict[str, bool], dict[str, Any]], str]

TERMINAL_EVENT_TYPES = {"task_completed", "task_dropped", "deadline_reached", "deadline_expired"}


def canonical_task_key(trace_id: str, episode_id: int, task_id: int | str) -> str:
    return f"{trace_id}:{episode_id}:{int(task_id)}"


def _sample_append(sample: list[dict[str, Any]], record: dict[str, Any], limit: int) -> None:
    if len(sample) < limit:
        sample.append(dict(record))


def _trace_enabled_environment(trainer, *, episode_length: int, seed: int):
    env = _build_environment(trainer.config, episode_length=episode_length, seed=seed)
    env.trace_config = LifecycleTraceConfig(trace_enabled=True)
    env.reset(seed=seed)
    return env


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
        "duplicate_terminal_event_count": 0,
        "duplicate_reward_event_count": 0,
        "reconciled": False,
        "terminal_event_source": None,
        "lifecycle_terminal_event_types": [],
        "absolute_deadline_slot": absolute_deadline_slot,
        "timeout_length": timeout_length,
        "task_size": task_size,
        "processing_density": processing_density,
    }


def _reward_event_source(event: dict[str, Any]) -> str:
    if event.get("reward") is not None:
        return "env_step_reward_with_finalized_task"
    if event.get("reward_available") is not None:
        return "env_step_info_reward_with_finalized_task"
    return "unrecoverable_missing_reward_event"


def _canonical_outcome_from_events(finalized_records: list[dict[str, Any]], pending_evidence: bool) -> str:
    outcomes = [str(record.get("terminal_outcome")) for record in finalized_records if record.get("terminal_outcome")]
    if "completed" in outcomes:
        return "completed"
    if "dropped" in outcomes:
        return "dropped"
    if pending_evidence:
        return "pending_at_horizon"
    return "unknown"


def _record_canonical_reward(task_record: dict[str, Any], canonical_outcome: str) -> float:
    if canonical_outcome not in {"completed", "dropped"}:
        return 0.0
    finalized_records = task_record.get("finalized_records", [])
    source_task = finalized_records[-1] if finalized_records else None
    if source_task is None:
        return 0.0
    if canonical_outcome == "completed" and source_task.get("completion_slot") is not None and source_task.get("arrival_slot") is not None:
        return -float(phi_private(int(source_task["completion_slot"]), int(source_task["arrival_slot"])))
    if canonical_outcome == "dropped":
        return -40.0
    return 0.0


def evaluate_policy_on_trace_bank_repaired(
    *,
    trainer,
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
    episode_reward_totals: list[float] = []
    episode_summaries: list[dict[str, Any]] = []
    task_records: dict[str, dict[str, Any]] = {}
    decision_records: list[dict[str, Any]] = []
    terminal_event_records: list[dict[str, Any]] = []
    reward_event_records: list[dict[str, Any]] = []
    raw_terminal_event_count = 0
    raw_reward_event_count = 0
    raw_reward_total = 0.0
    raw_lifecycle_terminal_event_count = 0
    reward_available_count = 0
    raw_reward_recovery_blocked = False
    terminal_event_recovery_blocked = False

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
                selected_action = normalize_action_name(policy_fn(state_tensor, legal_action_mask, context))
                if selected_action not in evaluation_action_distribution:
                    selected_action = normalize_action_name(selected_action) or selected_action
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
                    ),
                )
                record["decision_record"] = decision_record
                record["selected_action"] = selected_action
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
                        selected_action=normalize_action_name(event.get("selected_action")),
                        arrival_slot=int(event.get("arrival_slot", 0) or 0),
                        decision_slot=int(event.get("slot", 0) or 0),
                        absolute_deadline_slot=int(event.get("absolute_deadline_slot", 0) or 0),
                        timeout_length=None,
                        task_size=float(event.get("size_mbits", 0.0) or 0.0),
                        processing_density=float(event.get("processing_density_gcycles_per_mbit", 0.0) or 0.0),
                    ),
                )
                event_type = str(event.get("event_type"))
                if event_type in TERMINAL_EVENT_TYPES:
                    raw_lifecycle_terminal_event_count += 1
                    record["lifecycle_terminal_event_types"].append(event_type)
                if event_type == "reward_emitted":
                    reward_value = float(event.get("reward", 0.0) or 0.0)
                    reward_source = _reward_event_source(event)
                    reward_record = EvaluationRewardRecord(
                        trace_id=trace_id,
                        episode_id=episode_index,
                        task_id=int(task_id_value),
                        slot=int(event.get("slot", info.get("slot", env.current_slot))),
                        selected_action=normalize_action_name(event.get("selected_action")) or record.get("selected_action"),
                        terminal_outcome=str(event.get("terminal_outcome") or record.get("terminal_outcome") or "unknown"),
                        raw_reward=reward_value,
                        reward_event_source=reward_source,
                        reward_available=bool(event.get("reward_available", True)),
                    ).to_dict()
                    record["reward_event_records"].append(reward_record)
                    record["raw_reward_event_count"] += 1
                    record["raw_reward_total"] += reward_value
                    record["reward_available_from_step"] = bool(event.get("reward_available", True))
                    record["raw_reward_event_source"] = reward_source
                    reward_event_records.append(reward_record)
                    raw_reward_event_count += 1
                    raw_reward_total += reward_value
                    if reward_record["reward_available"]:
                        reward_available_count += 1
                    _sample_append(reward_samples, reward_record, record_sample_limit)

            finalized_tasks = info.get("finalized_tasks", [])
            for index, task in enumerate(finalized_tasks):
                task_key = canonical_task_key(trace_id, episode_index, task.get("task_id", 0))
                record = episode_records.setdefault(
                    task_key,
                    _empty_task_record(
                        trace_id=trace_id,
                        episode_id=episode_index,
                        task_id=int(task.get("task_id", 0)),
                        selected_action=normalize_action_name(task.get("selected_action")),
                        arrival_slot=int(task.get("arrival_slot", 0) or 0),
                        decision_slot=int(task.get("arrival_slot", 0) or 0),
                        absolute_deadline_slot=int(task.get("absolute_deadline_slot", 0) or 0),
                        timeout_length=int(task.get("timeout_length", 0) or 0),
                        task_size=float(task.get("size_mbits", 0.0) or 0.0),
                        processing_density=float(task.get("processing_density_gcycles_per_mbit", 0.0) or 0.0),
                    ),
                )
                terminal_outcome = str(task.get("terminal_outcome") or "unknown")
                completion_slot = task.get("completion_slot")
                arrival_slot = task.get("arrival_slot")
                latency_slots = int(completion_slot) - int(arrival_slot) + 1 if completion_slot is not None and arrival_slot is not None else None
                terminal_record = EvaluationTerminalRecord(
                    trace_id=trace_id,
                    episode_id=episode_index,
                    task_id=int(task.get("task_id", 0)),
                    slot=int(info.get("slot", env.current_slot)),
                    terminal_outcome=terminal_outcome,
                    selected_action=normalize_action_name(task.get("selected_action")) or selected_action,
                    arrival_slot=int(arrival_slot or 0),
                    completion_or_drop_slot=int(completion_slot) if completion_slot is not None else None,
                    latency_slots=latency_slots,
                    raw_reward_from_step=float(step_reward) if step_reward is not None else None,
                    reward_available_from_step=bool(task.get("reward_available", False)),
                    finalized_task_index=index,
                    event_source="env_step_finalized_tasks",
                ).to_dict()
                record["terminal_event_records"].append(terminal_record)
                record["finalized_records"].append(dict(task))
                if record["raw_terminal_event_count"] == 0:
                    record["raw_terminal_event_count"] = 1
                else:
                    record["duplicate_terminal_event_count"] += 1
                    record["raw_terminal_event_count"] += 1
                record["terminal_outcome"] = terminal_outcome
                record["terminal_slot"] = terminal_record["slot"]
                record["completion_or_drop_slot"] = terminal_record["completion_or_drop_slot"]
                record["latency_slots"] = terminal_record["latency_slots"]
                record["terminal_event_source"] = "env_step_finalized_tasks"
                terminal_event_records.append(terminal_record)
                raw_terminal_event_count += 1
                _sample_append(terminal_samples, terminal_record, record_sample_limit)
                if record["reward_event_records"]:
                    reward_value = float(record["reward_event_records"][-1]["raw_reward"])
                    record["terminal_event_records"][-1]["raw_reward_from_step"] = reward_value
                    record["terminal_event_records"][-1]["reward_available_from_step"] = bool(record["reward_event_records"][-1]["reward_available"])

            if terminated or truncated:
                break

        episode_raw_reward_total = 0.0
        episode_raw_reward_count = 0
        episode_terminal_count = 0
        episode_completion_count = 0
        episode_drop_count = 0
        episode_pending_count = 0
        episode_unknown_count = 0
        episode_canonical_reward_total = 0.0
        episode_canonical_reward_count = 0
        for record in episode_records.values():
            terminal_outcome = _canonical_outcome_from_events(record["finalized_records"], bool(record.get("pending_evidence")))
            canonical_reward = _record_canonical_reward(record, terminal_outcome)
            record["terminal_outcome"] = terminal_outcome
            record["canonical_reward"] = canonical_reward
            record["completion_or_drop_slot"] = record["completion_or_drop_slot"]
            record["raw_vs_canonical_reward_delta"] = float(record["raw_reward_total"]) - float(canonical_reward)
            record["duplicate_reward_event_count"] = max(0, int(record["raw_reward_event_count"]) - (1 if terminal_outcome in {"completed", "dropped"} else 0))
            record["duplicate_terminal_event_count"] = max(0, int(record["raw_terminal_event_count"]) - (1 if terminal_outcome in {"completed", "dropped"} else 0))
            record["reconciled"] = (
                (terminal_outcome in {"completed", "dropped"} and abs(float(record["raw_reward_total"]) - float(canonical_reward)) <= REWARD_RECONCILIATION_TOLERANCE)
                or (terminal_outcome in {"pending_at_horizon", "unknown"} and float(record["raw_reward_total"]) == 0.0 and float(canonical_reward) == 0.0)
            )
            episode_raw_reward_total += float(record["raw_reward_total"])
            episode_raw_reward_count += int(record["raw_reward_event_count"])
            if terminal_outcome in {"completed", "dropped"}:
                episode_terminal_count += 1
                episode_canonical_reward_total += float(canonical_reward)
                episode_canonical_reward_count += 1
                if terminal_outcome == "completed":
                    episode_completion_count += 1
                else:
                    episode_drop_count += 1
            elif terminal_outcome == "pending_at_horizon":
                episode_pending_count += 1
            else:
                episode_unknown_count += 1
            if record["decision_record"] is not None:
                record["selected_action"] = record["selected_action"] or record["decision_record"].get("selected_action")
            elif record["finalized_records"]:
                record["selected_action"] = record["selected_action"] or normalize_action_name(record["finalized_records"][-1].get("selected_action"))

        episode_reward_totals.append(episode_canonical_reward_total)
        episode_summaries.append(
            {
                "episode_id": episode_index,
                "trace_id": trace_id,
                "decision_count": episode_decision_count,
                "terminal_task_count": episode_terminal_count,
                "completion_count": episode_completion_count,
                "drop_count": episode_drop_count,
                "pending_count": episode_pending_count,
                "unknown_count": episode_unknown_count,
                "raw_reward_event_count": episode_raw_reward_count,
                "raw_reward_total": episode_raw_reward_total,
                "canonical_reward_total": episode_canonical_reward_total,
                "reward_recovered": episode_raw_reward_count > 0 or episode_canonical_reward_total == 0.0,
            }
        )
        task_records.update(episode_records)

    canonical_task_count = len(task_records)
    canonical_terminal_task_count = sum(1 for record in task_records.values() if record.get("terminal_outcome") in {"completed", "dropped"})
    canonical_task_reward_count = canonical_terminal_task_count
    canonical_task_reward_total = sum(float(record.get("canonical_reward", 0.0)) for record in task_records.values())
    completed_count = sum(1 for record in task_records.values() if record.get("terminal_outcome") == "completed")
    dropped_count = sum(1 for record in task_records.values() if record.get("terminal_outcome") == "dropped")
    pending_count = sum(1 for record in task_records.values() if record.get("terminal_outcome") == "pending_at_horizon")
    unknown_count = sum(1 for record in task_records.values() if record.get("terminal_outcome") == "unknown")
    raw_reward_event_recovery_blocked = raw_reward_event_count == 0 and canonical_task_reward_count > 0
    terminal_event_recovery_blocked = raw_terminal_event_count == 0 and canonical_terminal_task_count > 0
    if canonical_task_reward_count > 0 and raw_reward_event_count == 0:
        raw_reward_recovery_blocked = True
    if canonical_terminal_task_count > 0 and raw_terminal_event_count == 0:
        terminal_event_recovery_blocked = True

    evaluation_reward_summary = {
        "evaluation_episode_count": evaluation_episode_count,
        "mean_reward": sum(episode_reward_totals) / max(len(episode_reward_totals), 1),
        "completed_task_count": completed_count,
        "dropped_task_count": dropped_count,
        "pending_at_horizon_count": pending_count,
        "unknown_task_count": unknown_count,
        "terminal_transition_count": canonical_terminal_task_count,
        "reward_bearing_transition_count": canonical_task_reward_count,
        "canonical_task_count": canonical_task_count,
        "canonical_task_reward_total": canonical_task_reward_total,
        "canonical_task_reward_count": canonical_task_reward_count,
        "raw_terminal_event_count": raw_terminal_event_count,
        "raw_lifecycle_terminal_event_count": raw_lifecycle_terminal_event_count,
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
        "evaluation_action_by_episode_id": {
            str(summary["episode_id"]): summary for summary in episode_summaries
        },
        "decision_records_summary": {
            "decision_count": int(sum(evaluation_action_distribution.values())),
            "sample_records": decision_samples[:record_sample_limit],
            "evaluation_action_distribution_source": "evaluation_episodes",
        },
        "terminal_event_records": {
            "record_count": len(terminal_event_records),
            "sample_records": terminal_samples[:record_sample_limit],
            "recovered_from_finalized_tasks": True,
        },
        "reward_event_records": {
            "record_count": len(reward_event_records),
            "sample_records": reward_samples[:record_sample_limit],
            "reward_available_count": reward_available_count,
            "raw_reward_event_recovery_blocked": raw_reward_recovery_blocked,
        },
        "task_records": task_records,
        "episode_summaries": episode_summaries,
        "reward_reconciliation_tolerance": REWARD_RECONCILIATION_TOLERANCE,
        "raw_reward_event_recovery_blocked": raw_reward_recovery_blocked,
        "terminal_event_recovery_blocked": terminal_event_recovery_blocked,
        "raw_reward_event_count": raw_reward_event_count,
        "raw_reward_total": raw_reward_total,
        "raw_terminal_event_count": raw_terminal_event_count,
        "raw_lifecycle_terminal_event_count": raw_lifecycle_terminal_event_count,
        "episode_reward_totals": episode_reward_totals,
        "candidate_policy_vertical_share": float(evaluation_action_distribution.get("vertical", 0)) / max(float(sum(evaluation_action_distribution.values())), 1.0),
        "evaluation_reward_summary": evaluation_reward_summary,
    }


def build_policy_effect_after_repair(
    *,
    trainer,
    checkpoint_results: list[dict[str, Any]],
    fixed_policy_seed: int,
    evaluation_episode_count: int,
    episode_length: int,
    evaluation_trace_bank_id: str,
) -> dict[str, Any]:
    policy_results: dict[str, Any] = {}
    candidate_checkpoint_rewards: list[float] = []
    candidate_vertical_shares: list[float] = []

    for checkpoint in checkpoint_results:
        budget = int(checkpoint["training_budget"])
        candidate_key = f"candidate_policy_at_{budget}"
        candidate_result = dict(checkpoint["evaluation_policy_result"])
        candidate_result["evaluation_trace_bank_id"] = evaluation_trace_bank_id
        policy_results[candidate_key] = candidate_result
        candidate_checkpoint_rewards.append(
            float(candidate_result.get("evaluation_reward_summary", {}).get("mean_reward", candidate_result.get("mean_reward", 0.0)))
        )
        candidate_vertical_shares.append(
            float(candidate_result["evaluation_action_distribution"].get("vertical", 0))
            / max(float(candidate_result["evaluation_decision_count"]), 1.0)
        )

    for policy_name, policy_fn in build_fixed_policy_suite(fixed_policy_seed).items():
        policy_results[policy_name] = evaluate_policy_on_trace_bank_repaired(
            trainer=trainer,
            policy_name=policy_name,
            policy_fn=policy_fn,
            evaluation_episode_count=evaluation_episode_count,
            episode_length=episode_length,
            seed_base=trainer.config.seed_bundle.evaluation_trace_generation_seed,
            policy_kind="fixed",
            evaluation_trace_bank_id=evaluation_trace_bank_id,
        )

    reward_values = {
        policy_name: float(result.get("evaluation_reward_summary", {}).get("mean_reward", result.get("mean_reward", 0.0)))
        for policy_name, result in policy_results.items()
    }
    terminal_values = {
        policy_name: (
            int(result.get("evaluation_reward_summary", {}).get("completed_task_count", result.get("completed_count", 0))),
            int(result.get("evaluation_reward_summary", {}).get("dropped_task_count", result.get("dropped_count", 0))),
            int(result.get("evaluation_reward_summary", {}).get("pending_at_horizon_count", result.get("pending_at_horizon_count", 0))),
        )
        for policy_name, result in policy_results.items()
    }
    raw_reward_values = {
        policy_name: float(result.get("evaluation_reward_summary", {}).get("raw_event_reward_total", result.get("raw_reward_total", 0.0)))
        for policy_name, result in policy_results.items()
    }
    candidate_checkpoint_key = f"candidate_policy_at_{checkpoint_results[-1]['training_budget']}" if checkpoint_results else None
    candidate_vertical_collapse = False
    if candidate_checkpoint_key is not None:
        candidate_vertical_collapse = (
            float(policy_results[candidate_checkpoint_key]["evaluation_action_distribution"].get("vertical", 0))
            / max(float(policy_results[candidate_checkpoint_key]["evaluation_decision_count"]), 1.0)
            >= 0.95
        )

    reward_same_across_policies = len({round(value, 9) for value in reward_values.values()}) == 1
    terminal_same_across_policies = len(set(terminal_values.values())) == 1
    policy_affects_reward = "true" if not reward_same_across_policies else "false"
    policy_affects_terminal_outcomes = "true" if not terminal_same_across_policies else "false"
    evaluation_metric_static_because_reward_aggregation = "true" if reward_same_across_policies and len({tuple(result["evaluation_action_distribution"].items()) for result in policy_results.values()}) > 1 else "uncertain"
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
        "evaluation_metric_static_because_policy_same": "false",
        "evaluation_metric_static_because_reward_aggregation": evaluation_metric_static_because_reward_aggregation,
        "evaluation_metric_static_because_environment_dynamics": evaluation_metric_static_because_environment_dynamics,
        "evaluation_reward_static_after_instrumentation": reward_same_across_policies,
        "raw_event_reward_static_across_budget": len({round(value, 9) for value in raw_reward_values.values()}) == 1,
        "canonical_task_reward_static_across_budget": reward_same_across_policies,
        "canonical_completion_rate_static_across_budget": len(
            {
                float(result.get("evaluation_reward_summary", {}).get("completed_task_count", result.get("completed_count", 0)))
                / max(float(result.get("evaluation_reward_summary", {}).get("canonical_task_count", result.get("canonical_task_level_metrics", {}).get("canonical_task_count", 1))), 1.0)
                for result in policy_results.values()
            }
        ) == 1,
        "canonical_drop_rate_static_across_budget": len(
            {
                float(result.get("evaluation_reward_summary", {}).get("dropped_task_count", result.get("dropped_count", 0)))
                / max(float(result.get("evaluation_reward_summary", {}).get("canonical_task_count", result.get("canonical_task_level_metrics", {}).get("canonical_task_count", 1))), 1.0)
                for result in policy_results.values()
            }
        ) == 1,
        "evaluation_action_distribution_static_across_budget": len({tuple(result["evaluation_action_distribution"].items()) for result in policy_results.values()}) == 1,
        "policy_results": policy_results,
        "candidate_reward_variation": max(candidate_checkpoint_rewards) - min(candidate_checkpoint_rewards) if candidate_checkpoint_rewards else 0.0,
        "candidate_action_distribution_changed_by_budget": len({tuple(result["evaluation_action_distribution"].items()) for key, result in policy_results.items() if key.startswith("candidate_policy_at_")}) > 1,
        "candidate_terminal_outcomes_changed_by_budget": len({terminal_values[key] for key in policy_results if key.startswith("candidate_policy_at_")}) > 1,
        "canonical_policy_effect_summary": {
            "raw_event_reward_static_across_budget": len({round(value, 9) for value in raw_reward_values.values()}) == 1,
            "canonical_task_reward_static_across_budget": reward_same_across_policies,
            "canonical_completion_rate_static_across_budget": len(
                {
                    float(result.get("evaluation_reward_summary", {}).get("completed_task_count", result.get("completed_count", 0)))
                    / max(float(result.get("evaluation_reward_summary", {}).get("canonical_task_count", result.get("canonical_task_level_metrics", {}).get("canonical_task_count", 1))), 1.0)
                    for result in policy_results.values()
                }
            ) == 1,
            "canonical_drop_rate_static_across_budget": len(
                {
                    float(result.get("evaluation_reward_summary", {}).get("dropped_task_count", result.get("dropped_count", 0)))
                    / max(float(result.get("evaluation_reward_summary", {}).get("canonical_task_count", result.get("canonical_task_level_metrics", {}).get("canonical_task_count", 1))), 1.0)
                    for result in policy_results.values()
                }
            ) == 1,
            "evaluation_action_distribution_static_across_budget": len({tuple(result["evaluation_action_distribution"].items()) for result in policy_results.values()}) == 1,
            "policy_affects_reward": policy_affects_reward,
            "policy_affects_terminal_outcomes": policy_affects_terminal_outcomes,
        },
    }
