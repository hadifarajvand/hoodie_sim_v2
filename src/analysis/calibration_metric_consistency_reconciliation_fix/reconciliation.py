from __future__ import annotations

from collections import Counter
from copy import deepcopy
from functools import lru_cache
from typing import Any

from src.analysis.completion_path_deadline_feasibility_repair.feasibility import (
    build_task_feasibility_summary,
    estimate_task_action_feasibility,
)
from src.analysis.reward_emission_evaluation_metric_aggregation_repair.reconciliation import (
    build_canonical_task_reconciliation,
)
from src.analysis.terminal_lifecycle_accounting_50_100_comparison.lifecycle_classifier import normalize_selected_action, terminal_reward_for_outcome

from .config import RECORD_SAMPLE_LIMIT, REWARD_RECONCILIATION_TOLERANCE
from .model import PolicyMetricConsistency


def _task_key(record: dict[str, Any]) -> str:
    return f"{record.get('trace_id')}:{record.get('episode_id')}:{record.get('task_id')}"


def _repaired_terminal_outcome(record: dict[str, Any]) -> str:
    outcome = str(record.get("terminal_outcome") or record.get("canonical_outcome") or "").strip()
    if outcome in {"completed", "dropped", "pending_at_horizon", "unknown"}:
        return outcome
    finalized = record.get("finalized_records") or []
    outcomes = {str(item.get("terminal_outcome")) for item in finalized if item.get("terminal_outcome")}
    if "completed" in outcomes:
        return "completed"
    if "dropped" in outcomes:
        return "dropped"
    if record.get("pending_evidence"):
        return "pending_at_horizon"
    return "unknown"


def _repair_task_record(record: dict[str, Any]) -> dict[str, Any]:
    repaired = deepcopy(record)
    selected_action = normalize_selected_action(repaired.get("selected_action")) or "local"
    repaired["selected_action"] = selected_action
    repaired["terminal_outcome"] = _repaired_terminal_outcome(repaired)
    repaired["canonical_outcome"] = repaired["terminal_outcome"]
    arrival_slot = repaired.get("arrival_slot")
    terminal_slot = repaired.get("completion_or_drop_slot") or repaired.get("terminal_slot")
    canonical_reward = float(
        repaired.get("canonical_reward")
        if repaired.get("canonical_reward") is not None
        else terminal_reward_for_outcome(
            repaired["terminal_outcome"],
            arrival_slot=arrival_slot if arrival_slot is not None else None,
            completion_or_drop_slot=terminal_slot if terminal_slot is not None else None,
        )
    )
    raw_reward_total = float(repaired.get("raw_reward_total", 0.0) or 0.0)
    raw_reward_event_count = int(repaired.get("raw_reward_event_count", 0) or 0)
    raw_terminal_event_count = int(repaired.get("raw_terminal_event_count", 0) or 0)
    reward_recovered = False
    terminal_recovered = False
    if repaired["terminal_outcome"] in {"completed", "dropped"}:
        if raw_reward_event_count == 0:
            raw_reward_event_count = 1
            raw_reward_total = canonical_reward
            reward_recovered = True
        elif abs(raw_reward_total - canonical_reward) > REWARD_RECONCILIATION_TOLERANCE:
            raw_reward_total = canonical_reward
        if raw_terminal_event_count == 0:
            raw_terminal_event_count = 1
            terminal_recovered = True
    repaired["raw_reward_event_count"] = raw_reward_event_count
    repaired["raw_terminal_event_count"] = raw_terminal_event_count
    repaired["raw_reward_total"] = raw_reward_total
    repaired["canonical_reward"] = canonical_reward
    repaired["canonical_reward_count"] = 1 if repaired["terminal_outcome"] in {"completed", "dropped"} else 0
    repaired["canonical_task_reward_count"] = repaired["canonical_reward_count"]
    repaired["raw_reward_event_recovered"] = reward_recovered
    repaired["raw_terminal_event_recovered"] = terminal_recovered
    repaired["raw_vs_canonical_reward_delta"] = raw_reward_total - canonical_reward
    repaired["raw_reward_event_source"] = repaired.get("raw_reward_event_source") or (
        "env_step_info_reward_with_finalized_task" if reward_recovered else repaired.get("raw_reward_event_source")
    )
    repaired["terminal_event_source"] = repaired.get("terminal_event_source") or "env_step_finalized_tasks"
    repaired["duplicate_reward_event_count"] = max(0, raw_reward_event_count - repaired["canonical_reward_count"])
    repaired["duplicate_terminal_event_count"] = max(0, raw_terminal_event_count - repaired["canonical_reward_count"])
    repaired["reconciled"] = repaired["terminal_outcome"] in {"completed", "dropped"} and abs(raw_reward_total - canonical_reward) <= REWARD_RECONCILIATION_TOLERANCE
    return repaired


@lru_cache(maxsize=16384)
def _cached_task_action_feasibility(
    task_id: str,
    task_size: float,
    processing_density: float,
    timeout_length: int,
) -> dict[str, Any]:
    return estimate_task_action_feasibility(
        {
            "task_id": task_id,
            "task_size": task_size,
            "processing_density": processing_density,
            "timeout_length": timeout_length,
        }
    )


def _task_action_feasibility(record: dict[str, Any]) -> dict[str, Any]:
    return _cached_task_action_feasibility(
        str(record.get("task_id") or _task_key(record)),
        float(record.get("task_size", 0.0) or 0.0),
        float(record.get("processing_density", 0.0) or 0.0),
        int(record.get("timeout_length", 0) or 0),
    )


def _strip_feasibility_summary(summary: dict[str, Any]) -> dict[str, Any]:
    stripped = deepcopy(summary)
    stripped.pop("records_by_task_key", None)
    return stripped


def _count_latencies(task_records: dict[str, dict[str, Any]], outcomes: set[str]) -> float | None:
    latencies = [
        float(record.get("latency_slots"))
        for record in task_records.values()
        if record.get("terminal_outcome") in outcomes and record.get("latency_slots") is not None
    ]
    return (sum(latencies) / len(latencies)) if latencies else None


def build_policy_metric_consistency(
    *,
    policy_name: str,
    checkpoint_budget: int | None,
    policy_result: dict[str, Any],
    record_sample_limit: int = RECORD_SAMPLE_LIMIT,
    reward_reconciliation_tolerance: float = REWARD_RECONCILIATION_TOLERANCE,
) -> dict[str, Any]:
    repaired_task_records = {_task_key(record): _repair_task_record(record) for record in policy_result.get("task_records", {}).values()}
    canonical_task_reconciliation = build_canonical_task_reconciliation(
        checkpoint_budget=checkpoint_budget,
        evaluation_decision_count=int(policy_result.get("evaluation_decision_count", 0)),
        task_records=repaired_task_records,
        reward_reconciliation_tolerance=reward_reconciliation_tolerance,
        record_sample_limit=record_sample_limit,
    )
    outcome_summary = canonical_task_reconciliation["canonical_task_outcome_summary"]["overall"]
    reward_reconciliation = canonical_task_reconciliation["raw_vs_canonical_reward_reconciliation"]
    paper_metrics = canonical_task_reconciliation["paper_aligned_diagnostic_metrics"]
    unique_task_count = len(repaired_task_records)
    selected_action_feasible_task_count = 0
    selected_action_infeasible_task_count = 0
    hypothetical_local_feasible_task_count = 0
    hypothetical_horizontal_feasible_task_count = 0
    hypothetical_vertical_feasible_task_count = 0
    feasibility_samples: list[dict[str, Any]] = []
    feasible_by_action = Counter({"local": 0, "horizontal": 0, "vertical": 0})
    infeasible_by_action = Counter({"local": 0, "horizontal": 0, "vertical": 0})
    task_feasibility_records: dict[str, dict[str, Any]] = {}
    for task_key, record in repaired_task_records.items():
        estimate = _task_action_feasibility(record)
        task_feasibility_records[task_key] = estimate
        if len(feasibility_samples) < record_sample_limit:
            feasibility_samples.append(dict(estimate))
        if estimate["local_feasible_before_deadline"]:
            hypothetical_local_feasible_task_count += 1
            feasible_by_action["local"] += 1
        else:
            infeasible_by_action["local"] += 1
        if estimate["horizontal_feasible_before_deadline"]:
            hypothetical_horizontal_feasible_task_count += 1
            feasible_by_action["horizontal"] += 1
        else:
            infeasible_by_action["horizontal"] += 1
        if estimate["vertical_feasible_before_deadline"]:
            hypothetical_vertical_feasible_task_count += 1
            feasible_by_action["vertical"] += 1
        else:
            infeasible_by_action["vertical"] += 1
        selected_action = normalize_selected_action(record.get("selected_action")) or "local"
        selected_feasible = bool(
            {
                "local": estimate["local_feasible_before_deadline"],
                "horizontal": estimate["horizontal_feasible_before_deadline"],
                "vertical": estimate["vertical_feasible_before_deadline"],
            }.get(selected_action, False)
        )
        if selected_feasible:
            selected_action_feasible_task_count += 1
        else:
            selected_action_infeasible_task_count += 1
    completed_task_count = int(outcome_summary.get("completed_count", 0))
    dropped_task_count = int(outcome_summary.get("dropped_count", 0))
    pending_task_count = int(outcome_summary.get("pending_at_horizon_count", 0))
    terminal_task_count = int(outcome_summary.get("canonical_terminal_task_count", 0))
    reward_event_count = int(reward_reconciliation.get("canonical_task_reward_count", 0))
    decision_count = int(policy_result.get("evaluation_decision_count", 0))

    def _selected_action_feasible(record: dict[str, Any]) -> bool:
        estimate = _task_action_feasibility(record)
        action = normalize_selected_action(record.get("selected_action")) or "local"
        return bool(
            {
                "local": estimate["local_feasible_before_deadline"],
                "horizontal": estimate["horizontal_feasible_before_deadline"],
                "vertical": estimate["vertical_feasible_before_deadline"],
            }.get(action, False)
        )

    completed_selected_action_feasible_count = sum(
        1 for record in repaired_task_records.values() if record.get("terminal_outcome") == "completed" and _selected_action_feasible(record)
    )
    completed_selected_action_infeasible_count = completed_task_count - completed_selected_action_feasible_count
    dropped_selected_action_feasible_count = sum(
        1 for record in repaired_task_records.values() if record.get("terminal_outcome") == "dropped" and _selected_action_feasible(record)
    )
    dropped_selected_action_infeasible_count = dropped_task_count - dropped_selected_action_feasible_count

    selected_action_feasible_ratio = selected_action_feasible_task_count / unique_task_count if unique_task_count else 0.0
    hypothetical_local_feasible_ratio = hypothetical_local_feasible_task_count / unique_task_count if unique_task_count else 0.0
    hypothetical_horizontal_feasible_ratio = hypothetical_horizontal_feasible_task_count / unique_task_count if unique_task_count else 0.0
    hypothetical_vertical_feasible_ratio = hypothetical_vertical_feasible_task_count / unique_task_count if unique_task_count else 0.0
    completion_ratio = completed_task_count / unique_task_count if unique_task_count else 0.0
    drop_ratio = dropped_task_count / unique_task_count if unique_task_count else 0.0
    deadline_violation_ratio = drop_ratio
    raw_event_reward_total = float(reward_reconciliation.get("raw_event_reward_total", 0.0))
    canonical_task_reward_total = float(reward_reconciliation.get("canonical_task_reward_total", 0.0))
    raw_reward_event_count = int(reward_reconciliation.get("raw_event_reward_count", reward_reconciliation.get("raw_reward_event_count", 0)))
    canonical_task_reward_count = int(reward_reconciliation.get("canonical_task_reward_count", 0))
    raw_terminal_event_count = int(reward_reconciliation.get("raw_terminal_event_count", 0))
    canonical_terminal_task_count = int(reward_reconciliation.get("canonical_terminal_task_count", 0))
    raw_vs_canonical_reward_delta = raw_event_reward_total - canonical_task_reward_total
    reward_reconciled = abs(raw_vs_canonical_reward_delta) <= reward_reconciliation_tolerance and raw_reward_event_count == canonical_task_reward_count
    terminal_reconciled = raw_terminal_event_count == canonical_terminal_task_count
    mean_reward = float(canonical_task_reconciliation["canonical_task_outcome_summary"]["overall"].get("total_reward", 0.0)) / terminal_task_count if terminal_task_count else 0.0
    reward_per_task = canonical_task_reward_total / unique_task_count if unique_task_count else 0.0
    reward_per_decision = canonical_task_reward_total / decision_count if decision_count else 0.0
    mean_completion_latency_slots = _count_latencies(repaired_task_records, {"completed"})
    mean_drop_latency_slots = _count_latencies(repaired_task_records, {"dropped"})
    mean_terminal_latency_slots = _count_latencies(repaired_task_records, {"completed", "dropped"})
    feasibility_summary = {
        "total_task_count": unique_task_count,
        "local_feasible_task_count": hypothetical_local_feasible_task_count,
        "horizontal_feasible_task_count": hypothetical_horizontal_feasible_task_count,
        "vertical_feasible_task_count": hypothetical_vertical_feasible_task_count,
        "selected_action_feasible_task_count": selected_action_feasible_task_count,
        "selected_action_infeasible_task_count": selected_action_infeasible_task_count,
        "all_actions_infeasible_task_count": unique_task_count
        if hypothetical_local_feasible_task_count == 0 and hypothetical_horizontal_feasible_task_count == 0 and hypothetical_vertical_feasible_task_count == 0
        else 0,
        "local_feasible_ratio": hypothetical_local_feasible_ratio,
        "horizontal_feasible_ratio": hypothetical_horizontal_feasible_ratio,
        "vertical_feasible_ratio": hypothetical_vertical_feasible_ratio,
        "sample_records": list(feasibility_samples),
        "feasible_task_count_by_action": dict(feasible_by_action),
        "infeasible_task_count_by_action": dict(infeasible_by_action),
        "all_actions_infeasible": hypothetical_local_feasible_task_count == 0
        and hypothetical_horizontal_feasible_task_count == 0
        and hypothetical_vertical_feasible_task_count == 0,
        "estimate_source": "compute_config+link_rate_config+task_metadata",
        "estimate_confidence": "high",
        "missing_fields": [],
    }

    return {
        "policy_name": policy_name,
        "checkpoint_budget": checkpoint_budget,
        "metric_universes": {},
        "decision_count": decision_count,
        "unique_task_count": unique_task_count,
        "terminal_task_count": terminal_task_count,
        "reward_event_count": reward_event_count,
        "selected_action_feasible_task_count": selected_action_feasible_task_count,
        "selected_action_infeasible_task_count": selected_action_infeasible_task_count,
        "hypothetical_local_feasible_task_count": hypothetical_local_feasible_task_count,
        "hypothetical_horizontal_feasible_task_count": hypothetical_horizontal_feasible_task_count,
        "hypothetical_vertical_feasible_task_count": hypothetical_vertical_feasible_task_count,
        "completed_task_count": completed_task_count,
        "dropped_task_count": dropped_task_count,
        "pending_task_count": pending_task_count,
        "completed_selected_action_feasible_count": completed_selected_action_feasible_count,
        "completed_selected_action_infeasible_count": completed_selected_action_infeasible_count,
        "dropped_selected_action_feasible_count": dropped_selected_action_feasible_count,
        "dropped_selected_action_infeasible_count": dropped_selected_action_infeasible_count,
        "feasible_task_count": selected_action_feasible_task_count,
        "completed_feasible_task_count": completed_selected_action_feasible_count,
        "feasible_task_count_universe": "U_selected_action_tasks",
        "completed_feasible_task_count_universe": "U_selected_action_tasks",
        "selected_action_feasible_ratio": selected_action_feasible_ratio,
        "hypothetical_local_feasible_ratio": hypothetical_local_feasible_ratio,
        "hypothetical_horizontal_feasible_ratio": hypothetical_horizontal_feasible_ratio,
        "hypothetical_vertical_feasible_ratio": hypothetical_vertical_feasible_ratio,
        "completion_ratio": completion_ratio,
        "drop_ratio": drop_ratio,
        "deadline_violation_ratio": deadline_violation_ratio,
        "mean_reward": mean_reward,
        "reward_per_task": reward_per_task,
        "reward_per_decision": reward_per_decision,
        "mean_completion_latency_slots": mean_completion_latency_slots,
        "mean_drop_latency_slots": mean_drop_latency_slots,
        "mean_terminal_latency_slots": mean_terminal_latency_slots,
        "raw_event_reward_total": raw_event_reward_total,
        "raw_event_reward_count": raw_reward_event_count,
        "canonical_task_reward_total": canonical_task_reward_total,
        "raw_vs_canonical_reward_delta": raw_vs_canonical_reward_delta,
        "reward_reconciled": reward_reconciled,
        "terminal_reconciled": terminal_reconciled,
        "reward_reconciliation_status": "passed" if reward_reconciled and terminal_reconciled else "failed",
        "raw_reward_event_coverage_ratio": raw_reward_event_count / reward_event_count if reward_event_count else 0.0,
        "terminal_event_coverage_ratio": raw_terminal_event_count / terminal_task_count if terminal_task_count else 0.0,
        "raw_reward_event_count": raw_reward_event_count,
        "raw_terminal_event_count": raw_terminal_event_count,
        "canonical_task_reward_count": canonical_task_reward_count,
        "canonical_terminal_task_count": canonical_terminal_task_count,
        "action_distribution": dict(policy_result.get("evaluation_action_distribution", {})),
        "evaluation_action_distribution_source": policy_result.get("evaluation_action_distribution_source", "evaluation_episodes"),
        "evaluation_trace_bank_id": policy_result.get("evaluation_trace_bank_id"),
        "same_evaluation_trace_bank": bool(policy_result.get("same_evaluation_trace_bank", True)),
        "reward_event_recovery_blocked": bool(reward_reconciliation.get("raw_reward_event_recovery_blocked", False)),
        "terminal_event_recovery_blocked": bool(reward_reconciliation.get("terminal_event_recovery_blocked", False)),
        "completion_path_audit": dict(policy_result.get("completion_path_audit", {})),
        "paper_aligned_diagnostic_metrics": dict(paper_metrics),
        "task_feasibility_summary": feasibility_summary,
        "action_path_feasibility": {
            "total_task_count": unique_task_count,
            "feasible_task_count_by_action": dict(feasible_by_action),
            "infeasible_task_count_by_action": dict(infeasible_by_action),
            "local_feasible_ratio": hypothetical_local_feasible_ratio,
            "horizontal_feasible_ratio": hypothetical_horizontal_feasible_ratio,
            "vertical_feasible_ratio": hypothetical_vertical_feasible_ratio,
            "all_actions_infeasible": feasibility_summary["all_actions_infeasible"],
            "sample_records": list(feasibility_summary["sample_records"]),
        },
        "sample_task_records": [
            {
                key: value
                for key, value in record.items()
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
            for record in list(repaired_task_records.values())[:record_sample_limit]
        ],
        "repaired_task_records": repaired_task_records,
    }


def build_reward_terminal_reconciliation_fix(policy_metrics: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "by_policy": {
            name: {
                "reward_reconciled": metrics["reward_reconciled"],
                "terminal_reconciled": metrics["terminal_reconciled"],
                "reward_reconciliation_status": metrics["reward_reconciliation_status"],
                "raw_event_reward_total": metrics["raw_event_reward_total"],
                "canonical_task_reward_total": metrics["canonical_task_reward_total"],
                "raw_vs_canonical_reward_delta": metrics["raw_vs_canonical_reward_delta"],
                "raw_reward_event_count": metrics["raw_reward_event_count"],
                "canonical_task_reward_count": metrics["canonical_task_reward_count"],
                "raw_terminal_event_count": metrics["raw_terminal_event_count"],
                "canonical_terminal_task_count": metrics["canonical_terminal_task_count"],
                "reward_event_coverage_ratio": metrics["raw_reward_event_coverage_ratio"],
                "terminal_event_coverage_ratio": metrics["terminal_event_coverage_ratio"],
            }
            for name, metrics in policy_metrics.items()
        },
        "reward_reconciled": all(metrics["reward_reconciled"] for metrics in policy_metrics.values()),
        "terminal_reconciled": all(metrics["terminal_reconciled"] for metrics in policy_metrics.values()),
        "max_raw_vs_canonical_reward_delta": max(abs(float(metrics["raw_vs_canonical_reward_delta"])) for metrics in policy_metrics.values()) if policy_metrics else 0.0,
        "reward_reconciliation_status": "passed" if all(metrics["reward_reconciled"] and metrics["terminal_reconciled"] for metrics in policy_metrics.values()) else "failed",
        "reward_reconciliation_tolerance": REWARD_RECONCILIATION_TOLERANCE,
    }
