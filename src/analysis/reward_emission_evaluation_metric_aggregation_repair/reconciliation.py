from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from src.analysis.evaluation_instrumentation_reward_state_diagnostic.instrumented_evaluator import action_order, normalize_action_name

from .config import REWARD_RECONCILIATION_TOLERANCE, RECORD_SAMPLE_LIMIT


def _sample_append(sample: list[dict[str, Any]], record: dict[str, Any], limit: int) -> None:
    if len(sample) < limit:
        sample.append(dict(record))


def _empty_action_bucket() -> dict[str, Any]:
    return {
        "decision_count": 0,
        "completed_count": 0,
        "dropped_count": 0,
        "pending_at_horizon_count": 0,
        "unknown_count": 0,
        "terminal_transition_count": 0,
        "reward_bearing_transition_count": 0,
        "total_reward": 0.0,
        "mean_reward": 0.0,
        "completion_reward_count": 0,
        "drop_penalty_count": 0,
        "mean_completion_latency_slots": None,
        "mean_drop_latency_slots": None,
        "mean_terminal_latency_slots": None,
        "canonical_task_count": 0,
        "canonical_terminal_task_count": 0,
        "canonical_reward_total": 0.0,
        "canonical_reward_count": 0,
        "canonical_task_mean_reward": 0.0,
        "canonical_completion_ratio": 0.0,
        "canonical_drop_ratio": 0.0,
        "canonical_deadline_violation_ratio": 0.0,
        "canonical_pending_ratio": 0.0,
        "raw_terminal_event_count": 0,
        "raw_reward_emission_count": 0,
        "raw_event_reward_total": 0.0,
        "raw_event_reward_count": 0,
        "raw_vs_canonical_reward_delta": 0.0,
        "duplicate_terminal_event_count": 0,
        "duplicate_reward_event_count": 0,
        "double_count_detected": False,
        "_completion_latency_sum": 0.0,
        "_completion_latency_count": 0,
        "_drop_latency_sum": 0.0,
        "_drop_latency_count": 0,
        "_terminal_latency_sum": 0.0,
        "_terminal_latency_count": 0,
    }


def _finalize_action_bucket(bucket: dict[str, Any]) -> dict[str, Any]:
    bucket["mean_reward"] = bucket["total_reward"] / bucket["terminal_transition_count"] if bucket["terminal_transition_count"] else 0.0
    bucket["mean_completion_latency_slots"] = (
        bucket["_completion_latency_sum"] / bucket["_completion_latency_count"] if bucket["_completion_latency_count"] else None
    )
    bucket["mean_drop_latency_slots"] = bucket["_drop_latency_sum"] / bucket["_drop_latency_count"] if bucket["_drop_latency_count"] else None
    bucket["mean_terminal_latency_slots"] = (
        bucket["_terminal_latency_sum"] / bucket["_terminal_latency_count"] if bucket["_terminal_latency_count"] else None
    )
    bucket["canonical_task_mean_reward"] = (
        bucket["canonical_reward_total"] / bucket["canonical_reward_count"] if bucket["canonical_reward_count"] else 0.0
    )
    bucket["canonical_completion_ratio"] = bucket["completed_count"] / bucket["canonical_task_count"] if bucket["canonical_task_count"] else 0.0
    bucket["canonical_drop_ratio"] = bucket["dropped_count"] / bucket["canonical_task_count"] if bucket["canonical_task_count"] else 0.0
    bucket["canonical_deadline_violation_ratio"] = bucket["canonical_drop_ratio"]
    bucket["canonical_pending_ratio"] = bucket["pending_at_horizon_count"] / bucket["canonical_task_count"] if bucket["canonical_task_count"] else 0.0
    bucket["raw_vs_canonical_reward_delta"] = bucket["raw_event_reward_total"] - bucket["canonical_reward_total"]
    bucket["duplicate_terminal_event_count"] = max(0, int(bucket["raw_terminal_event_count"]) - int(bucket["canonical_terminal_task_count"]))
    bucket["duplicate_reward_event_count"] = max(0, int(bucket["raw_reward_emission_count"]) - int(bucket["canonical_reward_count"]))
    bucket["double_count_detected"] = bool(bucket["duplicate_terminal_event_count"] or bucket["duplicate_reward_event_count"])
    bucket.pop("_completion_latency_sum", None)
    bucket.pop("_completion_latency_count", None)
    bucket.pop("_drop_latency_sum", None)
    bucket.pop("_drop_latency_count", None)
    bucket.pop("_terminal_latency_sum", None)
    bucket.pop("_terminal_latency_count", None)
    return bucket


def _empty_reward_decomposition() -> dict[str, Any]:
    return {
        "reward_by_action": {action: 0.0 for action in action_order()},
        "reward_by_terminal_outcome": {"completed": 0.0, "dropped": 0.0},
        "reward_by_action_and_terminal_outcome": {
            action: {
                "completed": {
                    "count": 0,
                    "total_reward": 0.0,
                    "mean_reward": 0.0,
                    "raw_event_reward_total": 0.0,
                    "raw_event_reward_count": 0,
                    "canonical_task_reward_total": 0.0,
                    "canonical_task_reward_count": 0,
                    "canonical_task_mean_reward": 0.0,
                    "raw_vs_canonical_reward_delta": 0.0,
                },
                "dropped": {
                    "count": 0,
                    "total_reward": 0.0,
                    "mean_reward": 0.0,
                    "raw_event_reward_total": 0.0,
                    "raw_event_reward_count": 0,
                    "canonical_task_reward_total": 0.0,
                    "canonical_task_reward_count": 0,
                    "canonical_task_mean_reward": 0.0,
                    "raw_vs_canonical_reward_delta": 0.0,
                },
            }
            for action in action_order()
        },
        "drop_penalty_count_by_action": {action: 0 for action in action_order()},
        "completion_reward_count_by_action": {action: 0 for action in action_order()},
        "raw_event_reward_total_by_action": {action: 0.0 for action in action_order()},
        "raw_event_reward_count_by_action": {action: 0 for action in action_order()},
        "canonical_task_reward_total_by_action": {action: 0.0 for action in action_order()},
        "canonical_task_reward_count_by_action": {action: 0 for action in action_order()},
        "canonical_task_mean_reward_by_action": {action: 0.0 for action in action_order()},
        "raw_vs_canonical_reward_delta_by_action": {action: 0.0 for action in action_order()},
        "nan_reward_count": 0,
        "zero_reward_count": 0,
        "reward_available_count": 0,
    }


def _finalize_reward_decomposition(decomposition: dict[str, Any]) -> dict[str, Any]:
    for action in action_order():
        for outcome in ("completed", "dropped"):
            bucket = decomposition["reward_by_action_and_terminal_outcome"][action][outcome]
            bucket["mean_reward"] = bucket["total_reward"] / bucket["count"] if bucket["count"] else 0.0
            bucket["canonical_task_mean_reward"] = (
                bucket["canonical_task_reward_total"] / bucket["canonical_task_reward_count"] if bucket["canonical_task_reward_count"] else 0.0
            )
            bucket["raw_vs_canonical_reward_delta"] = bucket["raw_event_reward_total"] - bucket["canonical_task_reward_total"]
    decomposition["raw_vs_canonical_reward_delta_total"] = sum(
        decomposition["raw_event_reward_total_by_action"][action] - decomposition["canonical_task_reward_total_by_action"][action]
        for action in action_order()
    )
    return decomposition


def _empty_task_summary() -> dict[str, Any]:
    return {
        "canonical_task_count": 0,
        "canonical_terminal_task_count": 0,
        "canonical_completion_count": 0,
        "canonical_drop_count": 0,
        "canonical_pending_count": 0,
        "canonical_unknown_count": 0,
        "completed_count": 0,
        "dropped_count": 0,
        "pending_at_horizon_count": 0,
        "unknown_count": 0,
        "terminal_transition_count": 0,
        "reward_bearing_transition_count": 0,
        "total_reward": 0.0,
        "mean_reward": 0.0,
        "completion_reward_count": 0,
        "drop_penalty_count": 0,
        "raw_terminal_event_count": 0,
        "raw_reward_emission_count": 0,
        "raw_event_reward_total": 0.0,
        "raw_event_reward_count": 0,
        "canonical_task_reward_total": 0.0,
        "canonical_task_reward_count": 0,
        "canonical_task_mean_reward": 0.0,
        "raw_vs_canonical_reward_delta": 0.0,
        "duplicate_terminal_event_count": 0,
        "duplicate_reward_event_count": 0,
        "double_count_detected": False,
        "canonical_completion_ratio": 0.0,
        "canonical_drop_ratio": 0.0,
        "canonical_deadline_violation_ratio": 0.0,
        "canonical_pending_ratio": 0.0,
        "canonical_mean_completion_latency_slots": None,
        "canonical_mean_drop_latency_slots": None,
        "canonical_mean_terminal_latency_slots": None,
        "canonical_reward_per_task": 0.0,
        "canonical_reward_per_decision": 0.0,
        "canonical_tasks_per_decision": 0.0,
        "_completion_latency_sum": 0.0,
        "_completion_latency_count": 0,
        "_drop_latency_sum": 0.0,
        "_drop_latency_count": 0,
        "_terminal_latency_sum": 0.0,
        "_terminal_latency_count": 0,
    }


def _finalize_task_summary(bucket: dict[str, Any], *, decision_count: int) -> dict[str, Any]:
    bucket["canonical_task_mean_reward"] = (
        bucket["canonical_task_reward_total"] / bucket["canonical_task_reward_count"] if bucket["canonical_task_reward_count"] else 0.0
    )
    bucket["raw_vs_canonical_reward_delta"] = bucket["raw_event_reward_total"] - bucket["canonical_task_reward_total"]
    bucket["duplicate_terminal_event_count"] = max(0, int(bucket["raw_terminal_event_count"]) - int(bucket["canonical_task_reward_count"]))
    bucket["duplicate_reward_event_count"] = max(0, int(bucket["raw_reward_emission_count"]) - int(bucket["canonical_task_reward_count"]))
    bucket["double_count_detected"] = bool(bucket["duplicate_terminal_event_count"] or bucket["duplicate_reward_event_count"])
    bucket["canonical_completion_ratio"] = bucket["canonical_completion_count"] / bucket["canonical_task_count"] if bucket["canonical_task_count"] else 0.0
    bucket["canonical_drop_ratio"] = bucket["canonical_drop_count"] / bucket["canonical_task_count"] if bucket["canonical_task_count"] else 0.0
    bucket["canonical_deadline_violation_ratio"] = bucket["canonical_drop_ratio"]
    bucket["canonical_pending_ratio"] = bucket["canonical_pending_count"] / bucket["canonical_task_count"] if bucket["canonical_task_count"] else 0.0
    bucket["canonical_mean_completion_latency_slots"] = (
        bucket["_completion_latency_sum"] / bucket["_completion_latency_count"] if bucket["_completion_latency_count"] else None
    )
    bucket["canonical_mean_drop_latency_slots"] = bucket["_drop_latency_sum"] / bucket["_drop_latency_count"] if bucket["_drop_latency_count"] else None
    bucket["canonical_mean_terminal_latency_slots"] = (
        bucket["_terminal_latency_sum"] / bucket["_terminal_latency_count"] if bucket["_terminal_latency_count"] else None
    )
    bucket["canonical_reward_per_task"] = bucket["canonical_task_reward_total"] / bucket["canonical_task_count"] if bucket["canonical_task_count"] else 0.0
    bucket["canonical_reward_per_decision"] = bucket["canonical_task_reward_total"] / decision_count if decision_count else 0.0
    bucket["canonical_tasks_per_decision"] = bucket["canonical_task_count"] / decision_count if decision_count else 0.0
    bucket["canonical_reward_count"] = bucket["canonical_task_reward_count"]
    bucket["raw_reward_event_count"] = bucket["raw_reward_emission_count"]
    bucket.pop("_completion_latency_sum", None)
    bucket.pop("_completion_latency_count", None)
    bucket.pop("_drop_latency_sum", None)
    bucket.pop("_drop_latency_count", None)
    bucket.pop("_terminal_latency_sum", None)
    bucket.pop("_terminal_latency_count", None)
    return bucket


def _count_reward_coverage(task_records: dict[str, dict[str, Any]]) -> dict[str, int]:
    return {
        "reward_available_count": sum(1 for record in task_records.values() for event in record.get("reward_event_records", []) if event.get("reward_available")),
        "raw_reward_event_count": sum(int(record.get("raw_reward_event_count", 0)) for record in task_records.values()),
        "raw_terminal_event_count": sum(int(record.get("raw_terminal_event_count", 0)) for record in task_records.values()),
    }


def build_canonical_task_reconciliation(
    *,
    checkpoint_budget: int,
    evaluation_decision_count: int,
    task_records: dict[str, dict[str, Any]],
    reward_reconciliation_tolerance: float = REWARD_RECONCILIATION_TOLERANCE,
    record_sample_limit: int = RECORD_SAMPLE_LIMIT,
) -> dict[str, Any]:
    action_buckets = {action: _empty_action_bucket() for action in action_order()}
    reward_decomposition = _empty_reward_decomposition()
    canonical_task_outcomes: list[dict[str, Any]] = []
    sample_task_outcomes: list[dict[str, Any]] = []
    overall = _empty_task_summary()
    reward_coverage = _count_reward_coverage(task_records)

    for task_key, record in task_records.items():
        selected_action = normalize_action_name(record.get("selected_action")) or normalize_action_name(
            record.get("decision_record", {}).get("selected_action") if record.get("decision_record") else None
        ) or "local"
        if selected_action not in action_order():
            selected_action = "local"
        raw_reward_count = int(record.get("raw_reward_event_count", 0))
        raw_reward_total = float(record.get("raw_reward_total", 0.0))
        raw_terminal_count = int(record.get("raw_terminal_event_count", 0))
        arrival_slot = record.get("arrival_slot")
        decision_slot = record.get("first_decision_slot")
        completion_or_drop_slot = record.get("completion_or_drop_slot")
        latency_slots = record.get("latency_slots")
        finalized_records = record.get("finalized_records", [])
        terminal_outcomes = [str(finalized_record.get("terminal_outcome")) for finalized_record in finalized_records if finalized_record.get("terminal_outcome")]
        has_recovered_reward = raw_reward_count > 0 or raw_reward_total != 0.0
        if has_recovered_reward:
            if "completed" in terminal_outcomes:
                canonical_outcome = "completed"
            elif "dropped" in terminal_outcomes:
                canonical_outcome = "dropped"
            else:
                canonical_outcome = "unknown"
        elif finalized_records or record.get("pending_evidence"):
            canonical_outcome = "pending_at_horizon"
        else:
            canonical_outcome = "unknown"
        canonical_reward = float(record.get("canonical_reward", 0.0)) if has_recovered_reward and canonical_outcome in {"completed", "dropped"} else 0.0
        canonical_record = {
            "canonical_join_key": task_key,
            "trace_id": record.get("trace_id"),
            "episode_id": record.get("episode_id"),
            "task_id": record.get("task_id"),
            "selected_action": selected_action,
            "canonical_terminal_outcome": canonical_outcome,
            "first_decision_slot": decision_slot,
            "arrival_slot": arrival_slot,
            "terminal_slot": record.get("terminal_slot"),
            "completion_or_drop_slot": completion_or_drop_slot,
            "latency_slots": latency_slots,
            "canonical_reward": canonical_reward,
            "raw_reward_total": raw_reward_total,
            "raw_reward_event_count": raw_reward_count,
            "raw_terminal_event_count": raw_terminal_count,
            "raw_vs_canonical_reward_delta": raw_reward_total - canonical_reward,
            "duplicate_terminal_event_count": max(0, raw_terminal_count - (1 if canonical_outcome in {"completed", "dropped"} else 0)),
            "duplicate_reward_event_count": max(0, raw_reward_count - (1 if canonical_outcome in {"completed", "dropped"} else 0)),
            "reconciled": bool(
                (canonical_outcome in {"completed", "dropped"} and abs(raw_reward_total - canonical_reward) <= reward_reconciliation_tolerance and raw_reward_count > 0)
                or (canonical_outcome in {"pending_at_horizon", "unknown"} and raw_reward_count == 0 and raw_reward_total == 0.0 and canonical_reward == 0.0)
            ),
        }
        canonical_task_outcomes.append(canonical_record)
        _sample_append(sample_task_outcomes, canonical_record, record_sample_limit)

        bucket = action_buckets[selected_action]
        bucket["decision_count"] += 1
        bucket["canonical_task_count"] += 1
        bucket["raw_terminal_event_count"] += raw_terminal_count
        bucket["raw_reward_emission_count"] += raw_reward_count
        bucket["raw_event_reward_total"] += raw_reward_total
        bucket["raw_event_reward_count"] += raw_reward_count
        bucket["canonical_reward_total"] += canonical_reward
        if canonical_outcome in {"completed", "dropped"}:
            bucket["terminal_transition_count"] += 1
            bucket["reward_bearing_transition_count"] += 1
            bucket["canonical_terminal_task_count"] += 1
            bucket["canonical_reward_count"] += 1
            bucket["total_reward"] += canonical_reward
            bucket["reward_bearing_transition_count"] += 0
            if canonical_outcome == "completed":
                bucket["completed_count"] += 1
                bucket["completion_reward_count"] += 1
                if latency_slots is not None:
                    bucket["_completion_latency_sum"] += float(latency_slots)
                    bucket["_completion_latency_count"] += 1
                    bucket["_terminal_latency_sum"] += float(latency_slots)
                    bucket["_terminal_latency_count"] += 1
            else:
                bucket["dropped_count"] += 1
                bucket["drop_penalty_count"] += 1
                if latency_slots is not None:
                    bucket["_drop_latency_sum"] += float(latency_slots)
                    bucket["_drop_latency_count"] += 1
                    bucket["_terminal_latency_sum"] += float(latency_slots)
                    bucket["_terminal_latency_count"] += 1
            reward_decomposition["reward_by_action"][selected_action] += canonical_reward
            reward_decomposition["reward_by_terminal_outcome"][canonical_outcome] += canonical_reward
            reward_decomposition["reward_by_action_and_terminal_outcome"][selected_action][canonical_outcome]["count"] += 1
            reward_decomposition["reward_by_action_and_terminal_outcome"][selected_action][canonical_outcome]["total_reward"] += canonical_reward
            reward_decomposition["reward_by_action_and_terminal_outcome"][selected_action][canonical_outcome]["raw_event_reward_total"] += raw_reward_total
            reward_decomposition["reward_by_action_and_terminal_outcome"][selected_action][canonical_outcome]["raw_event_reward_count"] += raw_reward_count
            reward_decomposition["reward_by_action_and_terminal_outcome"][selected_action][canonical_outcome]["canonical_task_reward_total"] += canonical_reward
            reward_decomposition["reward_by_action_and_terminal_outcome"][selected_action][canonical_outcome]["canonical_task_reward_count"] += 1
            if canonical_outcome == "completed":
                reward_decomposition["completion_reward_count_by_action"][selected_action] += 1
            else:
                reward_decomposition["drop_penalty_count_by_action"][selected_action] += 1
        elif canonical_outcome == "pending_at_horizon":
            bucket["pending_at_horizon_count"] += 1
        else:
            bucket["unknown_count"] += 1
        reward_decomposition["raw_event_reward_total_by_action"][selected_action] += raw_reward_total
        reward_decomposition["raw_event_reward_count_by_action"][selected_action] += raw_reward_count
        reward_decomposition["canonical_task_reward_total_by_action"][selected_action] += canonical_reward
        reward_decomposition["canonical_task_reward_count_by_action"][selected_action] += 1 if canonical_outcome in {"completed", "dropped"} else 0
        reward_decomposition["canonical_task_mean_reward_by_action"][selected_action] = (
            reward_decomposition["canonical_task_reward_total_by_action"][selected_action]
            / reward_decomposition["canonical_task_reward_count_by_action"][selected_action]
            if reward_decomposition["canonical_task_reward_count_by_action"][selected_action]
            else 0.0
        )
        reward_decomposition["raw_vs_canonical_reward_delta_by_action"][selected_action] += raw_reward_total - canonical_reward

        overall["canonical_task_count"] += 1
        overall["raw_terminal_event_count"] += raw_terminal_count
        overall["raw_reward_emission_count"] += raw_reward_count
        overall["raw_event_reward_total"] += raw_reward_total
        overall["raw_event_reward_count"] += raw_reward_count
        overall["canonical_task_reward_total"] += canonical_reward
        if canonical_outcome in {"completed", "dropped"}:
            overall["canonical_terminal_task_count"] += 1
            overall["canonical_task_reward_count"] += 1
            overall["terminal_transition_count"] += 1
            overall["reward_bearing_transition_count"] += 1
            overall["total_reward"] += canonical_reward
            if canonical_outcome == "completed":
                overall["canonical_completion_count"] += 1
                overall["completed_count"] += 1
                overall["completion_reward_count"] += 1
                if latency_slots is not None:
                    overall["_completion_latency_sum"] += float(latency_slots)
                    overall["_completion_latency_count"] += 1
                    overall["_terminal_latency_sum"] += float(latency_slots)
                    overall["_terminal_latency_count"] += 1
            else:
                overall["canonical_drop_count"] += 1
                overall["dropped_count"] += 1
                overall["drop_penalty_count"] += 1
                if latency_slots is not None:
                    overall["_drop_latency_sum"] += float(latency_slots)
                    overall["_drop_latency_count"] += 1
                    overall["_terminal_latency_sum"] += float(latency_slots)
                    overall["_terminal_latency_count"] += 1
        elif canonical_outcome == "pending_at_horizon":
            overall["canonical_pending_count"] += 1
            overall["pending_at_horizon_count"] += 1
        else:
            overall["canonical_unknown_count"] += 1
            overall["unknown_count"] += 1

    for bucket in action_buckets.values():
        _finalize_action_bucket(bucket)
    _finalize_task_summary(overall, decision_count=evaluation_decision_count)
    _finalize_reward_decomposition(reward_decomposition)
    reward_decomposition["reward_available_count"] = reward_coverage["reward_available_count"]

    canonical_task_reward_total = overall["canonical_task_reward_total"]
    canonical_task_reward_count = overall["canonical_task_reward_count"]
    raw_event_reward_total = overall["raw_event_reward_total"]
    raw_event_reward_count = overall["raw_event_reward_count"]
    raw_terminal_event_count = overall["raw_terminal_event_count"]
    canonical_terminal_task_count = overall["canonical_terminal_task_count"]
    duplicate_terminal_event_count = max(0, raw_terminal_event_count - canonical_terminal_task_count)
    duplicate_reward_event_count = max(0, raw_event_reward_count - canonical_task_reward_count)
    raw_vs_canonical_reward_delta = raw_event_reward_total - canonical_task_reward_total
    reward_reconciled = abs(raw_vs_canonical_reward_delta) <= reward_reconciliation_tolerance and not (
        (canonical_task_reward_count > 0 and raw_event_reward_count == 0) or (canonical_terminal_task_count > 0 and raw_terminal_event_count == 0)
    )
    raw_reward_event_coverage_ratio = raw_event_reward_count / max(canonical_task_reward_count, 1)
    terminal_event_coverage_ratio = raw_terminal_event_count / max(canonical_terminal_task_count, 1)

    paper_aligned_diagnostic_metrics = {
        "training_budget": checkpoint_budget,
        "canonical_completion_ratio": overall["canonical_completion_ratio"],
        "canonical_drop_ratio": overall["canonical_drop_ratio"],
        "canonical_deadline_violation_ratio": overall["canonical_deadline_violation_ratio"],
        "canonical_pending_ratio": overall["canonical_pending_ratio"],
        "canonical_mean_completion_latency_slots": overall["canonical_mean_completion_latency_slots"],
        "canonical_mean_drop_latency_slots": overall["canonical_mean_drop_latency_slots"],
        "canonical_mean_terminal_latency_slots": overall["canonical_mean_terminal_latency_slots"],
        "canonical_reward_per_task": overall["canonical_reward_per_task"],
        "canonical_reward_per_decision": overall["canonical_reward_per_decision"],
        "canonical_tasks_per_decision": overall["canonical_tasks_per_decision"],
        "reward_reconciliation_status": "passed" if reward_reconciled else "failed",
        "raw_reward_event_coverage_ratio": raw_reward_event_coverage_ratio,
        "terminal_event_coverage_ratio": terminal_event_coverage_ratio,
    }

    raw_vs_canonical_reward_reconciliation = {
        "checkpoint_budget": checkpoint_budget,
        "raw_event_reward_total": raw_event_reward_total,
        "raw_event_reward_count": raw_event_reward_count,
        "raw_terminal_event_count": raw_terminal_event_count,
        "canonical_task_reward_total": canonical_task_reward_total,
        "canonical_task_reward_count": canonical_task_reward_count,
        "canonical_task_count": overall["canonical_task_count"],
        "canonical_terminal_task_count": canonical_terminal_task_count,
        "duplicate_terminal_event_count": duplicate_terminal_event_count,
        "duplicate_reward_event_count": duplicate_reward_event_count,
        "raw_vs_canonical_reward_delta": raw_vs_canonical_reward_delta,
        "reward_reconciled": reward_reconciled,
        "raw_reward_event_recovery_blocked": canonical_task_reward_count > 0 and raw_event_reward_count == 0,
        "terminal_event_recovery_blocked": canonical_terminal_task_count > 0 and raw_terminal_event_count == 0,
    }

    return {
        "checkpoint_budget": checkpoint_budget,
        "decision_count": evaluation_decision_count,
        "canonical_task_outcomes": canonical_task_outcomes,
        "canonical_task_outcome_sample": sample_task_outcomes,
        "canonical_task_outcome_summary": {
            "checkpoint_budget": checkpoint_budget,
            "overall": overall,
            "by_action": action_buckets,
            "reward_coverage": reward_coverage,
        },
        "canonical_reward_decomposition": reward_decomposition,
        "raw_vs_canonical_reward_reconciliation": raw_vs_canonical_reward_reconciliation,
        "paper_aligned_diagnostic_metrics": paper_aligned_diagnostic_metrics,
    }


def summarize_raw_vs_canonical_across_checkpoints(reconciliation_results: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "checkpoint_budgets": [result["checkpoint_budget"] for result in reconciliation_results],
        "by_checkpoint": [result["raw_vs_canonical_reward_reconciliation"] for result in reconciliation_results],
        "reward_reconciled": all(result["raw_vs_canonical_reward_reconciliation"]["reward_reconciled"] for result in reconciliation_results),
        "raw_reward_event_recovery_blocked": any(result["raw_vs_canonical_reward_reconciliation"]["raw_reward_event_recovery_blocked"] for result in reconciliation_results),
        "terminal_event_recovery_blocked": any(result["raw_vs_canonical_reward_reconciliation"]["terminal_event_recovery_blocked"] for result in reconciliation_results),
        "raw_vs_canonical_reward_delta_total": sum(
            result["raw_vs_canonical_reward_reconciliation"]["raw_vs_canonical_reward_delta"] for result in reconciliation_results
        ),
    }
