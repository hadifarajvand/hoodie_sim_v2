from __future__ import annotations

from typing import Any

from src.analysis.completion_path_deadline_feasibility_repair.feasibility import estimate_task_action_feasibility
from src.analysis.terminal_lifecycle_accounting_50_100_comparison.lifecycle_classifier import normalize_selected_action


def _feasible_task_ids_by_action(task_records: dict[str, dict[str, Any]]) -> dict[str, set[str]]:
    feasible: dict[str, set[str]] = {"local": set(), "horizontal": set(), "vertical": set()}
    for task_key, record in task_records.items():
        estimate = estimate_task_action_feasibility(record)
        if estimate["local_feasible_before_deadline"]:
            feasible["local"].add(task_key)
        if estimate["horizontal_feasible_before_deadline"]:
            feasible["horizontal"].add(task_key)
        if estimate["vertical_feasible_before_deadline"]:
            feasible["vertical"].add(task_key)
    return feasible


def build_action_path_diversity(task_records: dict[str, dict[str, Any]], *, checkpoint_budget: int) -> dict[str, Any]:
    feasible_ids = _feasible_task_ids_by_action(task_records)
    feasible_counts = {action: len(ids) for action, ids in feasible_ids.items()}
    count_based = len({count for count in feasible_counts.values()}) > 1
    pairwise_set_equality = {
        "local_horizontal": feasible_ids["local"] == feasible_ids["horizontal"],
        "local_vertical": feasible_ids["local"] == feasible_ids["vertical"],
        "horizontal_vertical": feasible_ids["horizontal"] == feasible_ids["vertical"],
    }
    pairwise_count_equality = {
        "local_horizontal": feasible_counts["local"] == feasible_counts["horizontal"],
        "local_vertical": feasible_counts["local"] == feasible_counts["vertical"],
        "horizontal_vertical": feasible_counts["horizontal"] == feasible_counts["vertical"],
    }
    set_based = not (pairwise_set_equality["local_horizontal"] and pairwise_set_equality["local_vertical"] and pairwise_set_equality["horizontal_vertical"])
    feasible_task_ids_by_action_sample = {action: sorted(ids)[:25] for action, ids in feasible_ids.items()}
    return {
        "checkpoint_budget": checkpoint_budget,
        "count_based_action_feasibility_diversity": count_based,
        "set_based_action_feasibility_diversity": set_based,
        "actions_have_different_feasibility": count_based or set_based,
        "feasible_task_count_by_action": feasible_counts,
        "feasible_task_set_sizes_by_action": {action: len(ids) for action, ids in feasible_ids.items()},
        "pairwise_set_equality": pairwise_set_equality,
        "pairwise_count_equality": pairwise_count_equality,
        "feasible_task_ids_by_action_sample": feasible_task_ids_by_action_sample,
    }
