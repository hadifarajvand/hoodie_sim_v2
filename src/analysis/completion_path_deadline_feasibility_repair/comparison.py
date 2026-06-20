from __future__ import annotations

from typing import Any


def _checkpoint_episode_count(checkpoint: dict[str, Any]) -> int:
    training_state = checkpoint.get("training_state", checkpoint)
    return int(
        checkpoint.get(
            "cumulative_training_episode_count",
            training_state.get("cumulative_training_episode_count", 0),
        )
    )


def build_checkpoint_50_100_feasibility_comparison(checkpoint_results: list[dict[str, Any]]) -> dict[str, Any]:
    by_checkpoint: list[dict[str, Any]] = []
    for checkpoint in checkpoint_results:
        evaluation = checkpoint["evaluation_policy_result"]
        policy_summary = checkpoint["candidate_policy_summary"]
        feasible_task_count_by_action = policy_summary.get("feasible_task_count_by_action", {})
        runtime_audit = policy_summary.get("runtime_event_audit", {})
        by_checkpoint.append(
            {
                "training_budget": int(checkpoint["training_budget"]),
                "cumulative_training_episode_count": _checkpoint_episode_count(checkpoint),
                "candidate_action_distribution": evaluation["evaluation_action_distribution"],
                "completion_count": int(evaluation["evaluation_reward_summary"]["completed_task_count"]),
                "drop_count": int(evaluation["evaluation_reward_summary"]["dropped_task_count"]),
                "pending_count": int(evaluation["evaluation_reward_summary"]["pending_at_horizon_count"]),
                "completion_ratio": float(policy_summary["completion_ratio"]),
                "drop_ratio": float(policy_summary["drop_ratio"]),
                "deadline_violation_ratio": float(policy_summary["deadline_violation_ratio"]),
                "mean_reward": float(policy_summary["mean_reward"]),
                "reward_per_task": float(policy_summary["reward_per_task"]),
                "reward_per_decision": float(policy_summary["reward_per_decision"]),
                "mean_terminal_latency_slots": policy_summary["mean_terminal_latency_slots"],
                "feasible_task_ratio": float(sum(int(count) for count in feasible_task_count_by_action.values()))
                / max(float(policy_summary["canonical_task_count"]), 1.0),
                "local_feasible_ratio": float(feasible_task_count_by_action.get("local", 0))
                / max(float(policy_summary["canonical_task_count"]), 1.0),
                "horizontal_feasible_ratio": float(feasible_task_count_by_action.get("horizontal", 0))
                / max(float(policy_summary["canonical_task_count"]), 1.0),
                "vertical_feasible_ratio": float(feasible_task_count_by_action.get("vertical", 0))
                / max(float(policy_summary["canonical_task_count"]), 1.0),
                "execution_progress_event_count": int(runtime_audit["execution_progress_event_count"]),
                "execution_completed_event_count": int(runtime_audit["execution_completed_event_count"]),
                "deadline_before_completion_count": int(runtime_audit["deadline_before_execution_completion_count"]),
                "terminal_event_coverage_ratio": float(policy_summary["terminal_event_coverage_ratio"]),
                "reward_event_coverage_ratio": float(policy_summary["reward_event_coverage_ratio"]),
                "raw_vs_canonical_reward_delta": float(
                    checkpoint["evaluation_policy_result"]["reward_reconciliation_after_terminal_repair"]["raw_vs_canonical_reward_delta"]
                ),
                "duplicate_terminal_event_count": int(
                    checkpoint["evaluation_policy_result"]["raw_vs_canonical_terminal_reconciliation"]["duplicate_terminal_event_count"]
                ),
                "duplicate_reward_event_count": int(
                    checkpoint["evaluation_policy_result"]["reward_reconciliation_after_terminal_repair"]["raw_event_reward_count"]
                    - checkpoint["evaluation_policy_result"]["reward_reconciliation_after_terminal_repair"]["canonical_task_reward_count"]
                ),
                "reward_reconciled": bool(checkpoint["evaluation_policy_result"]["reward_reconciliation_after_terminal_repair"]["reward_reconciled"]),
                "terminal_reconciled": bool(checkpoint["evaluation_policy_result"]["raw_vs_canonical_terminal_reconciliation"]["terminal_reconciled"]),
            }
        )
    if len(by_checkpoint) >= 2:
        first, second = by_checkpoint[0], by_checkpoint[1]
        comparison = {
            "budget_pair": [first["training_budget"], second["training_budget"]],
            "candidate_action_distribution_changed": first["candidate_action_distribution"] != second["candidate_action_distribution"],
            "completion_count_delta": int(second["completion_count"]) - int(first["completion_count"]),
            "drop_count_delta": int(second["drop_count"]) - int(first["drop_count"]),
            "pending_count_delta": int(second["pending_count"]) - int(first["pending_count"]),
            "completion_ratio_delta": float(second["completion_ratio"]) - float(first["completion_ratio"]),
            "drop_ratio_delta": float(second["drop_ratio"]) - float(first["drop_ratio"]),
            "deadline_violation_ratio_delta": float(second["deadline_violation_ratio"]) - float(first["deadline_violation_ratio"]),
            "reward_per_task_delta": float(second["reward_per_task"]) - float(first["reward_per_task"]),
            "reward_per_decision_delta": float(second["reward_per_decision"]) - float(first["reward_per_decision"]),
            "mean_terminal_latency_slots_delta": (
                None
                if first["mean_terminal_latency_slots"] is None or second["mean_terminal_latency_slots"] is None
                else float(second["mean_terminal_latency_slots"]) - float(first["mean_terminal_latency_slots"])
            ),
            "feasible_task_ratio_delta": float(second["feasible_task_ratio"]) - float(first["feasible_task_ratio"]),
            "local_feasible_ratio_delta": float(second["local_feasible_ratio"]) - float(first["local_feasible_ratio"]),
            "horizontal_feasible_ratio_delta": float(second["horizontal_feasible_ratio"]) - float(first["horizontal_feasible_ratio"]),
            "vertical_feasible_ratio_delta": float(second["vertical_feasible_ratio"]) - float(first["vertical_feasible_ratio"]),
            "execution_progress_event_count_delta": int(second["execution_progress_event_count"]) - int(first["execution_progress_event_count"]),
            "execution_completed_event_count_delta": int(second["execution_completed_event_count"]) - int(first["execution_completed_event_count"]),
            "deadline_before_completion_count_delta": int(second["deadline_before_completion_count"]) - int(first["deadline_before_completion_count"]),
        }
        if comparison["candidate_action_distribution_changed"] and (
            comparison["completion_count_delta"] == 0
            and comparison["drop_count_delta"] == 0
            and comparison["pending_count_delta"] == 0
        ):
            comparison_classification = "action_changed_but_outcome_static"
        elif any(
            abs(float(comparison[key])) > 1e-12
            for key in (
                "feasible_task_ratio_delta",
                "local_feasible_ratio_delta",
                "horizontal_feasible_ratio_delta",
                "vertical_feasible_ratio_delta",
            )
        ):
            comparison_classification = "feasibility_changed"
        elif any(
            abs(float(comparison[key])) > 1e-12
            for key in (
                "completion_count_delta",
                "drop_count_delta",
                "pending_count_delta",
                "reward_per_task_delta",
                "reward_per_decision_delta",
                "execution_progress_event_count_delta",
                "execution_completed_event_count_delta",
                "deadline_before_completion_count_delta",
            )
        ):
            comparison_classification = "completion_path_changed"
        else:
            comparison_classification = "no_change_between_50_and_100"
    else:
        comparison = {}
        comparison_classification = "no_change_between_50_and_100"
    return {
        "checkpoint_budgets": [checkpoint["training_budget"] for checkpoint in checkpoint_results],
        "by_checkpoint": by_checkpoint,
        "comparison": comparison,
        "comparison_classification": comparison_classification,
    }
