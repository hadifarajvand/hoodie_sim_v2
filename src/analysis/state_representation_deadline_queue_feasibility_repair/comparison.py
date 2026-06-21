from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from src.analysis.completion_path_deadline_feasibility_repair.feasibility import build_task_feasibility_summary

ACTION_ORDER = ("local", "horizontal", "vertical")
LEGACY_REPORT_PATH = Path("artifacts/analysis/calibration-metric-consistency-reconciliation-fix/calibration-metric-consistency-report.json")


def _load_json(path: Path) -> dict[str, Any]:
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def load_legacy_state_profile_report(path: Path = LEGACY_REPORT_PATH) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Legacy state profile report not found: {path}")
    return _load_json(path)


def _action_entropy(action_distribution: dict[str, int]) -> float:
    total = sum(int(v) for v in action_distribution.values())
    if total <= 0:
        return 0.0
    entropy = 0.0
    for action in ACTION_ORDER:
        count = int(action_distribution.get(action, 0))
        if count <= 0:
            continue
        probability = count / total
        entropy -= probability * math.log2(probability)
    return entropy


def _dominant_action_stats(action_distribution: dict[str, int]) -> dict[str, Any]:
    total = sum(int(v) for v in action_distribution.values())
    if total <= 0:
        return {
            "action_entropy": 0.0,
            "dominant_action_share": 0.0,
            "is_action_collapsed": False,
            "dominant_action_name": None,
        }
    dominant_action_name = max(ACTION_ORDER, key=lambda action: int(action_distribution.get(action, 0)))
    dominant_action_share = int(action_distribution.get(dominant_action_name, 0)) / total
    return {
        "action_entropy": _action_entropy(action_distribution),
        "dominant_action_share": dominant_action_share,
        "is_action_collapsed": dominant_action_share >= 0.95,
        "dominant_action_name": dominant_action_name,
    }


def _summary_from_policy_result(policy_name: str, checkpoint_budget: int | None, policy_result: dict[str, Any]) -> dict[str, Any]:
    reward_fix = dict(policy_result.get("reward_reconciliation_after_terminal_repair", {}))
    terminal_fix = dict(policy_result.get("raw_vs_canonical_terminal_reconciliation", {}))
    reward_summary = dict(policy_result.get("evaluation_reward_summary", {}))
    action_distribution = dict(policy_result.get("evaluation_action_distribution", {}))
    decision_count = int(policy_result.get("evaluation_decision_count", 0))
    task_records = dict(policy_result.get("task_records", {}))
    feasibility = build_task_feasibility_summary(task_records, record_sample_limit=25)
    unique_task_count = int(reward_summary.get("canonical_task_count", len(task_records)))
    completed_count = int(reward_summary.get("completed_task_count", 0))
    dropped_count = int(reward_summary.get("dropped_task_count", 0))
    pending_count = int(reward_summary.get("pending_at_horizon_count", 0))
    total_reward = float(reward_summary.get("canonical_task_reward_total", 0.0))
    feasible_task_count = int(feasibility.get("selected_action_feasible_task_count", 0))
    infeasible_task_count = int(feasibility.get("selected_action_infeasible_task_count", 0))
    completed_feasible_count = 0
    dropped_feasible_count = 0
    completed_infeasible_count = 0
    dropped_infeasible_count = 0
    for key, record in task_records.items():
        record_feasibility = dict(feasibility.get("records_by_task_key", {}).get(key, {}))
        selected_action = str(record.get("selected_action") or record_feasibility.get("selected_action") or "")
        selected_feasible = bool(
            {
                "local": record_feasibility.get("local_feasible_before_deadline"),
                "compute_local": record_feasibility.get("local_feasible_before_deadline"),
                "horizontal": record_feasibility.get("horizontal_feasible_before_deadline"),
                "offload_horizontal": record_feasibility.get("horizontal_feasible_before_deadline"),
                "vertical": record_feasibility.get("vertical_feasible_before_deadline"),
                "offload_vertical": record_feasibility.get("vertical_feasible_before_deadline"),
            }.get(selected_action, False)
        )
        if record.get("terminal_outcome") == "completed":
            if selected_feasible:
                completed_feasible_count += 1
            else:
                completed_infeasible_count += 1
        elif record.get("terminal_outcome") == "dropped":
            if selected_feasible:
                dropped_feasible_count += 1
            else:
                dropped_infeasible_count += 1
    summary = {
        "policy_name": policy_name,
        "checkpoint_budget": checkpoint_budget,
        "decision_count": decision_count,
        "unique_task_count": unique_task_count,
        "action_distribution": action_distribution,
        "selected_action_feasible_task_count": feasible_task_count,
        "selected_action_infeasible_task_count": infeasible_task_count,
        "selected_action_feasible_ratio": feasible_task_count / unique_task_count if unique_task_count else 0.0,
        "completed_selected_action_feasible_count": completed_feasible_count,
        "completed_selected_action_infeasible_count": completed_infeasible_count,
        "dropped_selected_action_feasible_count": dropped_feasible_count,
        "dropped_selected_action_infeasible_count": dropped_infeasible_count,
        "completed_count": completed_count,
        "dropped_count": dropped_count,
        "pending_count": pending_count,
        "completion_ratio": completed_count / unique_task_count if unique_task_count else 0.0,
        "drop_ratio": dropped_count / unique_task_count if unique_task_count else 0.0,
        "deadline_violation_ratio": dropped_count / unique_task_count if unique_task_count else 0.0,
        "mean_reward": float(reward_summary.get("mean_reward", 0.0)),
        "reward_per_task": total_reward / unique_task_count if unique_task_count else 0.0,
        "reward_per_decision": total_reward / decision_count if decision_count else 0.0,
        "mean_completion_latency_slots": _mean_from_task_records(policy_result, "completed"),
        "mean_drop_latency_slots": _mean_from_task_records(policy_result, "dropped"),
        "mean_terminal_latency_slots": _mean_terminal_latency(policy_result),
        "reward_reconciled": bool(reward_fix.get("reward_reconciled", False)),
        "terminal_reconciled": bool(terminal_fix.get("terminal_reconciled", False)),
        "raw_vs_canonical_reward_delta": float(reward_fix.get("raw_vs_canonical_reward_delta", 0.0)),
        "feasible_task_count": feasible_task_count,
        "infeasible_task_count": infeasible_task_count,
        "selected_action_feasible_task_count_universe": "U_selected_action_tasks",
        "feasible_task_count_universe": "U_selected_action_tasks",
        "completed_feasible_task_count": completed_feasible_count,
        "completed_feasible_task_count_universe": "U_selected_action_tasks",
        "completed_infeasible_task_count": completed_infeasible_count,
        "dropped_feasible_task_count": dropped_feasible_count,
        "dropped_infeasible_task_count": dropped_infeasible_count,
        **_dominant_action_stats(action_distribution),
    }
    return summary


def _mean_from_task_records(policy_result: dict[str, Any], outcome: str) -> float | None:
    records = [
        float(record.get("latency_slots"))
        for record in policy_result.get("task_records", {}).values()
        if record.get("terminal_outcome") == outcome and record.get("latency_slots") is not None
    ]
    return (sum(records) / len(records)) if records else None


def _mean_terminal_latency(policy_result: dict[str, Any]) -> float | None:
    records = [
        float(record.get("latency_slots"))
        for record in policy_result.get("task_records", {}).values()
        if record.get("terminal_outcome") in {"completed", "dropped"} and record.get("latency_slots") is not None
    ]
    return (sum(records) / len(records)) if records else None


def build_policy_summaries(policy_results: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    summaries: dict[str, dict[str, Any]] = {}
    for policy_name, policy_result in policy_results.items():
        checkpoint_budget = policy_result.get("checkpoint_budget")
        summaries[policy_name] = _summary_from_policy_result(policy_name, checkpoint_budget, policy_result)
    return summaries


def build_state_profile_50_100_comparison(policy_summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    candidate_50 = policy_summaries["candidate_policy_at_50"]
    candidate_100 = policy_summaries["candidate_policy_at_100"]
    comparison = {
        "50_to_100_action_distribution_changed": candidate_50["action_distribution"] != candidate_100["action_distribution"],
        "50_to_100_completion_changed": candidate_50["completed_count"] != candidate_100["completed_count"],
        "50_to_100_drop_changed": candidate_50["dropped_count"] != candidate_100["dropped_count"],
        "50_to_100_reward_changed": candidate_50["reward_per_task"] != candidate_100["reward_per_task"],
        "50_to_100_selected_action_feasibility_changed": candidate_50["selected_action_feasible_ratio"] != candidate_100["selected_action_feasible_ratio"],
        "selected_action_feasible_ratio_delta": candidate_100["selected_action_feasible_ratio"] - candidate_50["selected_action_feasible_ratio"],
        "completion_ratio_delta": candidate_100["completion_ratio"] - candidate_50["completion_ratio"],
        "drop_ratio_delta": candidate_100["drop_ratio"] - candidate_50["drop_ratio"],
        "reward_per_task_delta": candidate_100["reward_per_task"] - candidate_50["reward_per_task"],
        "reward_per_decision_delta": candidate_100["reward_per_decision"] - candidate_50["reward_per_decision"],
        "mean_terminal_latency_slots_delta": (candidate_100["mean_terminal_latency_slots"] or 0.0) - (candidate_50["mean_terminal_latency_slots"] or 0.0),
    }
    if comparison["50_to_100_completion_changed"] or comparison["50_to_100_drop_changed"]:
        comparison_classification = "completion_path_changed"
    elif comparison["50_to_100_action_distribution_changed"]:
        comparison_classification = "action_changed_but_outcome_static"
    else:
        comparison_classification = "no_change_between_50_and_100"
    return {
        "checkpoint_budgets": [50, 100],
        "by_checkpoint": [candidate_50, candidate_100],
        "comparison": comparison,
        "comparison_classification": comparison_classification,
    }


def build_action_collapse_diagnostics(legacy_policy_100: dict[str, Any], new_policy_100: dict[str, Any]) -> dict[str, Any]:
    legacy_stats = _dominant_action_stats(dict(legacy_policy_100.get("action_distribution", {})))
    new_stats = _dominant_action_stats(dict(new_policy_100.get("action_distribution", {})))
    return {
        "legacy_state_dim": 3,
        "new_state_dim": 30,
        "legacy": legacy_stats,
        "new_state": new_stats,
        "action_collapse_reduced": bool(new_stats["dominant_action_share"] < legacy_stats["dominant_action_share"]),
    }


def build_selected_action_feasibility_diagnostics(legacy_policy_100: dict[str, Any], new_policy_100: dict[str, Any]) -> dict[str, Any]:
    legacy_ratio = float(legacy_policy_100.get("selected_action_feasible_ratio", 0.0))
    new_ratio = float(new_policy_100.get("selected_action_feasible_ratio", 0.0))
    return {
        "legacy_selected_action_feasible_ratio": legacy_ratio,
        "new_state_selected_action_feasible_ratio": new_ratio,
        "selected_action_feasible_ratio_delta": new_ratio - legacy_ratio,
        "completed_selected_action_feasible_delta": int(new_policy_100.get("completed_count", 0)) - int(legacy_policy_100.get("completed_count", 0)),
        "dropped_selected_action_infeasible_delta": int(new_policy_100.get("dropped_count", 0)) - int(legacy_policy_100.get("dropped_count", 0)),
    }


def build_legacy_vs_new_state_profile_comparison(
    legacy_report: dict[str, Any],
    new_state_audit: dict[str, Any],
    policy_summaries: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    legacy_comparison = list(legacy_report.get("consistent_50_100_comparison", {}).get("by_checkpoint", []))
    legacy_candidate_50 = legacy_comparison[0] if len(legacy_comparison) > 0 else {}
    legacy_candidate_100 = legacy_comparison[1] if len(legacy_comparison) > 1 else {}
    new_candidate_50 = policy_summaries.get("candidate_policy_at_50", {})
    new_candidate_100 = policy_summaries.get("candidate_policy_at_100", {})
    return {
        "legacy_state_dim": int(legacy_report.get("legacy_state_dim", 3)),
        "new_state_dim": int(new_state_audit.get("new_state_dim", 30)),
        "legacy_candidate_50": legacy_candidate_50,
        "legacy_candidate_100": legacy_candidate_100,
        "new_candidate_50": new_candidate_50,
        "new_candidate_100": new_candidate_100,
        "comparison": {
            "state_dim_increased": int(new_state_audit.get("new_state_dim", 30)) > int(legacy_report.get("legacy_state_dim", 3)),
            "action_distribution_changed": legacy_candidate_100.get("candidate_action_distribution") != new_candidate_100.get("action_distribution"),
            "selected_action_feasibility_improved": float(new_candidate_100.get("selected_action_feasible_ratio", 0.0))
            > float(legacy_candidate_100.get("selected_action_feasible_ratio", 0.0)),
            "action_collapse_reduced": float(new_candidate_100.get("dominant_action_share", 0.0))
            < float(legacy_candidate_100.get("dominant_action_share", 0.0)),
            "completion_ratio_changed": float(new_candidate_100.get("completion_ratio", 0.0))
            != float(legacy_candidate_100.get("completion_ratio", 0.0)),
            "reward_changed": float(new_candidate_100.get("reward_per_task", 0.0)) != float(legacy_candidate_100.get("reward_per_task", 0.0)),
        },
    }


def build_reconciliation_after_state_repair(policy_summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    reward_reconciled = all(bool(summary.get("reward_reconciled", False)) for summary in policy_summaries.values())
    terminal_reconciled = all(bool(summary.get("terminal_reconciled", False)) for summary in policy_summaries.values())
    max_delta = max(abs(float(summary.get("raw_vs_canonical_reward_delta", 0.0))) for summary in policy_summaries.values()) if policy_summaries else 0.0
    return {
        "reward_reconciliation_passed": reward_reconciled,
        "terminal_reconciliation_passed": terminal_reconciled,
        "raw_vs_canonical_reward_delta_max": max_delta,
        "policies_with_reward_reconciled_false": [name for name, summary in policy_summaries.items() if not bool(summary.get("reward_reconciled", False))],
        "policies_with_terminal_reconciled_false": [name for name, summary in policy_summaries.items() if not bool(summary.get("terminal_reconciled", False))],
    }
