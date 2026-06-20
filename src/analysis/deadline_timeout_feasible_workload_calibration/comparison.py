from __future__ import annotations

from typing import Any


def build_checkpoint_50_100_calibrated_comparison(checkpoint_results: list[dict[str, Any]], policy_effect: dict[str, Any], task_feasibility_summary: dict[str, Any]) -> dict[str, Any]:
    by_checkpoint: list[dict[str, Any]] = []
    candidate_50 = policy_effect["policy_summaries"]["candidate_policy_at_50"]
    candidate_100 = policy_effect["policy_summaries"]["candidate_policy_at_100"]
    for checkpoint in checkpoint_results:
        budget = int(checkpoint["training_budget"])
        summary = checkpoint["candidate_policy_summary"]
        by_checkpoint.append(
            {
                "training_budget": budget,
                "cumulative_training_episode_count": int(checkpoint["training_state"]["cumulative_training_episode_count"]),
                "feasible_task_ratio": float(task_feasibility_summary.get("overall_feasible_task_ratio", 0.0)),
                "local_feasible_ratio": float(task_feasibility_summary.get("local_feasible_ratio", 0.0)),
                "horizontal_feasible_ratio": float(task_feasibility_summary.get("horizontal_feasible_ratio", 0.0)),
                "vertical_feasible_ratio": float(task_feasibility_summary.get("vertical_feasible_ratio", 0.0)),
                "candidate_action_distribution": dict(summary.get("action_distribution", {})),
                "completion_count": int(summary.get("completed_count", 0)),
                "drop_count": int(summary.get("dropped_count", 0)),
                "pending_count": int(summary.get("pending_count", 0)),
                "completion_ratio": float(summary.get("completion_ratio", 0.0)),
                "drop_ratio": float(summary.get("drop_ratio", 0.0)),
                "deadline_violation_ratio": float(summary.get("deadline_violation_ratio", 0.0)),
                "reward_per_task": float(summary.get("reward_per_task", 0.0)),
                "reward_per_decision": float(summary.get("reward_per_decision", 0.0)),
                "mean_terminal_latency_slots": summary.get("mean_terminal_latency_slots"),
            }
        )
    first, second = by_checkpoint
    comparison = {
        "budget_pair": [first["training_budget"], second["training_budget"]],
        "candidate_action_distribution_changed": first["candidate_action_distribution"] != second["candidate_action_distribution"],
        "completion_count_delta": second["completion_count"] - first["completion_count"],
        "drop_count_delta": second["drop_count"] - first["drop_count"],
        "pending_count_delta": second["pending_count"] - first["pending_count"],
        "completion_ratio_delta": second["completion_ratio"] - first["completion_ratio"],
        "drop_ratio_delta": second["drop_ratio"] - first["drop_ratio"],
        "deadline_violation_ratio_delta": second["deadline_violation_ratio"] - first["deadline_violation_ratio"],
        "reward_per_task_delta": second["reward_per_task"] - first["reward_per_task"],
        "reward_per_decision_delta": second["reward_per_decision"] - first["reward_per_decision"],
        "mean_terminal_latency_slots_delta": (second["mean_terminal_latency_slots"] or 0.0) - (first["mean_terminal_latency_slots"] or 0.0),
        "feasible_task_ratio_delta": second["feasible_task_ratio"] - first["feasible_task_ratio"],
        "local_feasible_ratio_delta": second["local_feasible_ratio"] - first["local_feasible_ratio"],
        "horizontal_feasible_ratio_delta": second["horizontal_feasible_ratio"] - first["horizontal_feasible_ratio"],
        "vertical_feasible_ratio_delta": second["vertical_feasible_ratio"] - first["vertical_feasible_ratio"],
        "50_to_100_action_distribution_changed": first["candidate_action_distribution"] != second["candidate_action_distribution"],
        "50_to_100_completion_changed": first["completion_count"] != second["completion_count"],
        "50_to_100_drop_changed": first["drop_count"] != second["drop_count"],
        "50_to_100_reward_changed": first["reward_per_task"] != second["reward_per_task"],
    }
    if comparison["completion_count_delta"] == 0 and comparison["drop_count_delta"] == 0 and comparison["reward_per_task_delta"] == 0:
        comparison_classification = "action_changed_but_outcome_static" if comparison["candidate_action_distribution_changed"] else "no_change_between_50_and_100"
    elif comparison["completion_count_delta"] != 0 or comparison["drop_count_delta"] != 0:
        comparison_classification = "completion_path_changed"
    else:
        comparison_classification = "feasibility_changed"
    return {
        "checkpoint_budgets": [first["training_budget"], second["training_budget"]],
        "by_checkpoint": by_checkpoint,
        "comparison": comparison,
        "comparison_classification": comparison_classification,
        "candidate_policy_at_50": candidate_50,
        "candidate_policy_at_100": candidate_100,
    }

