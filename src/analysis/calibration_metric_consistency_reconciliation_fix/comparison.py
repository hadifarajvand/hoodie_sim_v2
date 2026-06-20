from __future__ import annotations

from typing import Any


def build_consistent_50_100_comparison(policy_effect: dict[str, Any], task_feasibility_summary: dict[str, Any]) -> dict[str, Any]:
    by_checkpoint: list[dict[str, Any]] = []
    for budget_key in ("candidate_policy_at_50", "candidate_policy_at_100"):
        summary = policy_effect["policy_summaries"][budget_key]
        by_checkpoint.append(
            {
                "training_budget": 50 if budget_key.endswith("_50") else 100,
                "candidate_action_distribution": dict(summary["action_distribution"]),
                "decision_count": int(summary["decision_count"]),
                "unique_task_count": int(summary["unique_task_count"]),
                "terminal_task_count": int(summary["terminal_task_count"]),
                "reward_event_count": int(summary["reward_event_count"]),
                "selected_action_feasible_task_count": int(summary["selected_action_feasible_task_count"]),
                "selected_action_infeasible_task_count": int(summary["selected_action_infeasible_task_count"]),
                "completion_count": int(summary["completed_task_count"]),
                "drop_count": int(summary["dropped_task_count"]),
                "pending_count": int(summary["pending_task_count"]),
                "completion_ratio": float(summary["completion_ratio"]),
                "drop_ratio": float(summary["drop_ratio"]),
                "deadline_violation_ratio": float(summary["deadline_violation_ratio"]),
                "reward_per_task": float(summary["reward_per_task"]),
                "reward_per_decision": float(summary["reward_per_decision"]),
                "mean_terminal_latency_slots": summary["mean_terminal_latency_slots"],
                "mean_completion_latency_slots": summary["mean_completion_latency_slots"],
                "mean_drop_latency_slots": summary["mean_drop_latency_slots"],
                "selected_action_feasible_ratio": float(summary["selected_action_feasible_ratio"]),
                "hypothetical_local_feasible_ratio": float(summary["hypothetical_local_feasible_ratio"]),
                "hypothetical_horizontal_feasible_ratio": float(summary["hypothetical_horizontal_feasible_ratio"]),
                "hypothetical_vertical_feasible_ratio": float(summary["hypothetical_vertical_feasible_ratio"]),
                "feasible_task_ratio": float(summary["selected_action_feasible_ratio"]),
                "local_feasible_ratio": float(task_feasibility_summary.get("local_feasible_ratio", 0.0)),
                "horizontal_feasible_ratio": float(task_feasibility_summary.get("horizontal_feasible_ratio", 0.0)),
                "vertical_feasible_ratio": float(task_feasibility_summary.get("vertical_feasible_ratio", 0.0)),
            }
        )
    first, second = by_checkpoint
    comparison = {
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
        "selected_action_feasible_ratio_delta": second["selected_action_feasible_ratio"] - first["selected_action_feasible_ratio"],
        "hypothetical_local_feasible_ratio_delta": second["hypothetical_local_feasible_ratio"] - first["hypothetical_local_feasible_ratio"],
        "hypothetical_horizontal_feasible_ratio_delta": second["hypothetical_horizontal_feasible_ratio"] - first["hypothetical_horizontal_feasible_ratio"],
        "hypothetical_vertical_feasible_ratio_delta": second["hypothetical_vertical_feasible_ratio"] - first["hypothetical_vertical_feasible_ratio"],
        "50_to_100_action_distribution_changed": first["candidate_action_distribution"] != second["candidate_action_distribution"],
        "50_to_100_completion_changed": first["completion_count"] != second["completion_count"],
        "50_to_100_drop_changed": first["drop_count"] != second["drop_count"],
        "50_to_100_reward_changed": first["reward_per_task"] != second["reward_per_task"],
        "50_to_100_selected_action_feasibility_changed": first["selected_action_feasible_ratio"] != second["selected_action_feasible_ratio"],
    }
    if comparison["completion_count_delta"] == 0 and comparison["drop_count_delta"] == 0 and comparison["reward_per_task_delta"] == 0:
        comparison_classification = "action_changed_but_outcome_static" if comparison["candidate_action_distribution_changed"] else "no_change_between_50_and_100"
    elif comparison["completion_count_delta"] != 0 or comparison["drop_count_delta"] != 0:
        comparison_classification = "completion_path_changed"
    else:
        comparison_classification = "feasibility_changed"
    return {
        "checkpoint_budgets": [50, 100],
        "by_checkpoint": by_checkpoint,
        "comparison": comparison,
        "comparison_classification": comparison_classification,
    }


def build_before_after_consistency_comparison(
    *,
    before_report: dict[str, Any],
    after_policy_effect: dict[str, Any],
    after_action_diversity: dict[str, Any],
    after_reconciliation: dict[str, Any],
    after_policy_metrics: dict[str, Any],
) -> dict[str, Any]:
    before_policy_effect = before_report.get("calibrated_policy_effect_comparison", {})
    before_candidate_100 = before_policy_effect.get("policy_summaries", {}).get("candidate_policy_at_100", {})
    before_candidate_50 = before_policy_effect.get("policy_summaries", {}).get("candidate_policy_at_50", {})
    before = {
        "actions_have_different_feasibility": bool(before_report.get("actions_have_different_feasibility", False)),
        "reward_reconciliation_status": before_candidate_100.get("reward_reconciliation_status"),
        "terminal_reconciled": before_candidate_100.get("terminal_reconciled"),
        "reward_reconciled": before_candidate_100.get("reward_reconciled"),
        "raw_vs_canonical_reward_delta": before_candidate_100.get("raw_vs_canonical_reward_delta"),
        "feasible_task_count": before_candidate_100.get("feasible_task_count"),
        "completed_feasible_task_count": before_candidate_100.get("completed_feasible_task_count"),
        "feasible_task_count_universe": "unknown" if before_candidate_100.get("feasible_task_count") is None else "not_explicitly_stated",
        "completed_feasible_task_count_universe": "unknown" if before_candidate_100.get("completed_feasible_task_count") is None else "not_explicitly_stated",
    }
    after_candidate_100 = after_policy_effect["policy_summaries"]["candidate_policy_at_100"]
    after = {
        "actions_have_different_feasibility": bool(after_action_diversity["actions_have_different_feasibility"]),
        "reward_reconciliation_status": after_candidate_100["reward_reconciliation_status"],
        "terminal_reconciled": after_candidate_100["terminal_reconciled"],
        "reward_reconciled": after_candidate_100["reward_reconciled"],
        "raw_vs_canonical_reward_delta": after_candidate_100["raw_vs_canonical_reward_delta"],
        "feasible_task_count": after_candidate_100["feasible_task_count"],
        "completed_feasible_task_count": after_candidate_100["completed_feasible_task_count"],
        "feasible_task_count_universe": after_candidate_100["feasible_task_count_universe"],
        "completed_feasible_task_count_universe": after_candidate_100["completed_feasible_task_count_universe"],
    }
    comparison = {
        "actions_have_different_feasibility_changed": before["actions_have_different_feasibility"] != after["actions_have_different_feasibility"],
        "reward_reconciliation_fixed": before["reward_reconciled"] is not True and after["reward_reconciled"] is True,
        "terminal_reconciliation_fixed": before["terminal_reconciled"] is not True and after["terminal_reconciled"] is True,
        "reward_delta_fixed": before["raw_vs_canonical_reward_delta"] != after["raw_vs_canonical_reward_delta"],
        "feasible_task_count_universe_explicit": after["feasible_task_count_universe"] == "U_selected_action_tasks",
        "completed_feasible_task_count_universe_explicit": after["completed_feasible_task_count_universe"] == "U_selected_action_tasks",
        "reward_reconciled": after_reconciliation["reward_reconciled"],
        "terminal_reconciled": after_reconciliation["terminal_reconciled"],
    }
    return {"before": before, "after": after, "comparison": comparison}
