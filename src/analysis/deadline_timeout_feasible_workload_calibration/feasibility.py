from __future__ import annotations

from typing import Any

from src.analysis.completion_path_deadline_feasibility_repair.feasibility import (
    build_action_path_feasibility as _build_action_path_feasibility,
    build_task_feasibility_summary as _build_task_feasibility_summary,
)


def load_before_baseline_metrics(path) -> dict[str, Any]:
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def build_calibrated_task_feasibility_summary(task_records: dict[str, dict[str, Any]], *, record_sample_limit: int) -> dict[str, Any]:
    summary = _build_task_feasibility_summary(task_records, record_sample_limit=record_sample_limit)
    summary["overall_feasible_task_ratio"] = (
        float(summary["total_task_count"] - summary["all_actions_infeasible_task_count"]) / max(float(summary["total_task_count"]), 1.0)
    )
    return summary


def build_calibrated_action_path_feasibility(task_feasibility_summary: dict[str, Any]) -> dict[str, Any]:
    action_path = _build_action_path_feasibility(task_feasibility_summary)
    action_path["overall_feasible_task_ratio"] = float(task_feasibility_summary.get("overall_feasible_task_ratio", 0.0))
    return action_path


def build_before_after_feasibility_comparison(before_report: dict[str, Any], after_task_summary: dict[str, Any], after_action_path: dict[str, Any], after_checkpoint: dict[str, Any]) -> dict[str, Any]:
    before_task_summary = before_report["task_feasibility_summary"]
    before_candidate = before_report["checkpoint_metrics"][-1]["candidate_policy_summary"]
    before_action_path = before_report["action_path_feasibility"]
    after_candidate = after_checkpoint["candidate_policy_summary"]
    return {
        "before_overall_feasible_task_ratio": float(before_task_summary.get("feasible_task_ratio", 0.0)),
        "after_overall_feasible_task_ratio": float(after_task_summary.get("overall_feasible_task_ratio", 0.0)),
        "before_completion_count": int(before_candidate.get("completed_count", 0)),
        "after_completion_count": int(after_candidate.get("completed_count", 0)),
        "before_drop_ratio": float(before_candidate.get("drop_ratio", 0.0)),
        "after_drop_ratio": float(after_candidate.get("drop_ratio", 0.0)),
        "before_deadline_violation_ratio": float(before_candidate.get("deadline_violation_ratio", 0.0)),
        "after_deadline_violation_ratio": float(after_candidate.get("deadline_violation_ratio", 0.0)),
        "before_action_path_feasibility": before_action_path,
        "after_action_path_feasibility": after_action_path,
    }

