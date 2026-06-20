from __future__ import annotations

from collections import Counter
from typing import Any


def _event_count_map(policy_result: dict[str, Any]) -> dict[str, int]:
    events = policy_result.get("terminal_event_classification", {}).get("overall", {}).get("event_type_counts", {})
    return {str(key): int(value) for key, value in events.items()}


def _policy_runtime_audit(policy_name: str, policy_result: dict[str, Any], task_feasibility_summary: dict[str, Any]) -> dict[str, Any]:
    event_counts = _event_count_map(policy_result)
    task_records = policy_result.get("task_records", {})
    feasible_lookup = task_feasibility_summary.get("records_by_task_key", {})

    positive_progress_tasks = 0
    zero_progress_tasks = 0
    execution_progress_without_completion = 0
    transmission_completed_without_execution = 0
    execution_started_without_progress = 0
    deadline_before_execution_completion = 0
    deadline_before_transmission_completion = 0
    remaining_cycles_at_drop = 0

    for task_key, record in task_records.items():
        lifecycle_event_types = set(record.get("lifecycle_event_types", []))
        terminal_outcome = str(record.get("terminal_outcome") or "unknown")
        has_progress = "execution_progress" in lifecycle_event_types
        has_execution_started = "execution_started" in lifecycle_event_types
        has_execution_completed = "execution_completed" in lifecycle_event_types
        has_transmission_started = "transmission_started" in lifecycle_event_types
        has_transmission_completed = "transmission_completed" in lifecycle_event_types

        if has_progress:
            positive_progress_tasks += 1
        else:
            zero_progress_tasks += 1
        if has_progress and not has_execution_completed:
            execution_progress_without_completion += 1
        if has_transmission_completed and not has_execution_started:
            transmission_completed_without_execution += 1
        if has_execution_started and not has_progress:
            execution_started_without_progress += 1
        if terminal_outcome == "dropped" and not has_execution_completed:
            deadline_before_execution_completion += 1
        if terminal_outcome == "dropped" and has_transmission_started and not has_transmission_completed:
            deadline_before_transmission_completion += 1
        feasibility = feasible_lookup.get(task_key, {})
        selected_action = str(record.get("selected_action") or "")
        action_feasible = {
            "local": bool(feasibility.get("local_feasible_before_deadline", False)),
            "compute_local": bool(feasibility.get("local_feasible_before_deadline", False)),
            "horizontal": bool(feasibility.get("horizontal_feasible_before_deadline", False)),
            "offload_horizontal": bool(feasibility.get("horizontal_feasible_before_deadline", False)),
            "vertical": bool(feasibility.get("vertical_feasible_before_deadline", False)),
            "offload_vertical": bool(feasibility.get("vertical_feasible_before_deadline", False)),
        }.get(selected_action, False)
        if terminal_outcome == "dropped" and not action_feasible:
            remaining_cycles_at_drop += 1

    canonical_task_count = len(task_records)
    return {
        "policy_name": policy_name,
        "decision_count": int(policy_result.get("evaluation_decision_count", 0)),
        "transmission_started_event_count": int(event_counts.get("transmission_started", 0)),
        "transmission_completed_event_count": int(event_counts.get("transmission_completed", 0)),
        "execution_started_event_count": int(event_counts.get("execution_started", 0)),
        "execution_progress_event_count": int(event_counts.get("execution_progress", 0)),
        "execution_completed_event_count": int(event_counts.get("execution_completed", 0)),
        "task_completed_event_count": int(event_counts.get("task_completed", 0)),
        "deadline_reached_event_count": int(event_counts.get("deadline_reached", 0)),
        "deadline_expired_event_count": int(event_counts.get("deadline_expired", 0)),
        "task_dropped_event_count": int(event_counts.get("task_dropped", 0)),
        "reward_emitted_event_count": int(event_counts.get("reward_emitted", 0)),
        "pending_at_horizon_count": int(event_counts.get("pending_at_horizon", 0)),
        "execution_progress_without_completion_count": int(execution_progress_without_completion),
        "transmission_completed_without_execution_count": int(transmission_completed_without_execution),
        "execution_started_without_progress_count": int(execution_started_without_progress),
        "deadline_before_execution_completion_count": int(deadline_before_execution_completion),
        "deadline_before_transmission_completion_count": int(deadline_before_transmission_completion),
        "tasks_with_positive_execution_progress_count": int(positive_progress_tasks),
        "tasks_with_zero_execution_progress_count": int(zero_progress_tasks),
        "tasks_with_remaining_cycles_at_drop_count": int(remaining_cycles_at_drop),
        "canonical_task_count": canonical_task_count,
    }


def build_runtime_event_path_audit(
    policy_results: dict[str, dict[str, Any]],
    task_feasibility_summary: dict[str, Any],
    *,
    checkpoint_results: list[dict[str, Any]] | None = None,
    overall_policy_name: str = "candidate_policy_at_100",
) -> dict[str, Any]:
    by_checkpoint: list[dict[str, Any]] = []
    if checkpoint_results is not None:
        for checkpoint in checkpoint_results:
            policy_name = f"candidate_policy_at_{int(checkpoint['training_budget'])}"
            policy_result = checkpoint["evaluation_policy_result"]
            by_checkpoint.append(
                {
                    "training_budget": int(checkpoint["training_budget"]),
                    "policy_name": policy_name,
                    **_policy_runtime_audit(policy_name, policy_result, task_feasibility_summary),
                }
            )
    by_policy = {
        policy_name: _policy_runtime_audit(policy_name, policy_result, task_feasibility_summary)
        for policy_name, policy_result in policy_results.items()
    }
    overall = dict(by_policy.get(overall_policy_name, next(iter(by_policy.values()), {})))
    overall["by_policy"] = {}
    return {
        "by_checkpoint": by_checkpoint,
        "overall_policy_name": overall_policy_name,
        "overall": overall,
        "by_policy": by_policy,
    }
