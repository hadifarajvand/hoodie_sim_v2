from __future__ import annotations

from typing import Any

from .universe import build_metric_universe_definitions
from .config import RECORD_SAMPLE_LIMIT
from .reconciliation import build_policy_metric_consistency

POLICY_ORDER = (
    "candidate_policy_at_50",
    "candidate_policy_at_100",
    "fixed_local_policy",
    "fixed_horizontal_policy",
    "fixed_vertical_policy",
    "random_legal_policy",
)

FIXED_POLICY_ORDER = ("fixed_local_policy", "fixed_horizontal_policy", "fixed_vertical_policy", "random_legal_policy")


def build_consistent_policy_effect_comparison(*, raw_payload: dict[str, Any], record_sample_limit: int = RECORD_SAMPLE_LIMIT) -> dict[str, Any]:
    raw_policy_effect = raw_payload["calibrated_policy_effect_comparison"]
    raw_policy_results = raw_policy_effect["policy_results"]
    policy_results: dict[str, dict[str, Any]] = {}
    for policy_name in POLICY_ORDER:
        raw_result = raw_policy_results[policy_name]
        checkpoint_budget = int(raw_result.get("checkpoint_budget")) if raw_result.get("checkpoint_budget") is not None else None
        policy_result = build_policy_metric_consistency(
            policy_name=policy_name,
            checkpoint_budget=checkpoint_budget,
            policy_result=raw_result,
            record_sample_limit=record_sample_limit,
        )
        policy_result["metric_universes"] = build_metric_universe_definitions()
        policy_results[policy_name] = {
            key: value
            for key, value in policy_result.items()
            if key != "repaired_task_records"
        }

    policy_summaries = {
        policy_name: {
            key: value
            for key, value in metrics.items()
            if key
            in {
                "policy_name",
                "checkpoint_budget",
                "decision_count",
                "unique_task_count",
                "terminal_task_count",
                "reward_event_count",
                "selected_action_feasible_task_count",
                "selected_action_infeasible_task_count",
                "hypothetical_local_feasible_task_count",
                "hypothetical_horizontal_feasible_task_count",
                "hypothetical_vertical_feasible_task_count",
                "completed_task_count",
                "dropped_task_count",
                "pending_task_count",
                "completed_selected_action_feasible_count",
                "completed_selected_action_infeasible_count",
                "dropped_selected_action_feasible_count",
                "dropped_selected_action_infeasible_count",
                "feasible_task_count",
                "completed_feasible_task_count",
                "feasible_task_count_universe",
                "completed_feasible_task_count_universe",
                "selected_action_feasible_ratio",
                "hypothetical_local_feasible_ratio",
                "hypothetical_horizontal_feasible_ratio",
                "hypothetical_vertical_feasible_ratio",
                "completion_ratio",
                "drop_ratio",
                "deadline_violation_ratio",
                "mean_reward",
                "reward_per_task",
                "reward_per_decision",
                "mean_completion_latency_slots",
                "mean_drop_latency_slots",
                "mean_terminal_latency_slots",
                "raw_event_reward_total",
                "raw_event_reward_count",
                "canonical_task_reward_total",
                "raw_vs_canonical_reward_delta",
                "reward_reconciled",
                "terminal_reconciled",
                "reward_reconciliation_status",
                "raw_reward_event_coverage_ratio",
                "terminal_event_coverage_ratio",
                "raw_reward_event_count",
                "raw_terminal_event_count",
                "canonical_task_reward_count",
                "canonical_terminal_task_count",
                "action_distribution",
                "evaluation_action_distribution_source",
                "evaluation_trace_bank_id",
                "same_evaluation_trace_bank",
                "reward_event_recovery_blocked",
                "terminal_event_recovery_blocked",
            }
        }
        for policy_name, metrics in policy_results.items()
    }
    candidate_50 = policy_results["candidate_policy_at_50"]
    candidate_100 = policy_results["candidate_policy_at_100"]
    fixed_policy_summaries = {policy_name: policy_summaries[policy_name] for policy_name in FIXED_POLICY_ORDER}
    any_fixed_policy_completes = any(summary["completed_task_count"] > 0 for summary in fixed_policy_summaries.values())
    candidate_100_replay = bool(
        raw_payload["calibrated_policy_effect_comparison"].get("candidate_policy_vertical_collapse_in_training_replay_window", False)
    )
    reward_values = {policy_name: float(summary["mean_reward"]) for policy_name, summary in policy_summaries.items()}
    terminal_values = {
        policy_name: (
            int(summary["completed_task_count"]),
            int(summary["dropped_task_count"]),
            int(summary["pending_task_count"]),
        )
        for policy_name, summary in policy_summaries.items()
    }
    reward_same_across_policies = len({round(value, 9) for value in reward_values.values()}) == 1
    terminal_same_across_policies = len(set(terminal_values.values())) == 1

    return {
        "evaluation_trace_bank_id": raw_payload["calibrated_policy_effect_comparison"].get("evaluation_trace_bank_id"),
        "evaluation_episode_count": raw_payload["calibrated_policy_effect_comparison"].get("evaluation_episode_count", 100),
        "episode_length": raw_payload["calibrated_policy_effect_comparison"].get("episode_length", 110),
        "raw_event_reward_static_across_budget": float(candidate_50["raw_event_reward_total"]) == float(candidate_100["raw_event_reward_total"]),
        "canonical_task_reward_static_across_budget": float(candidate_50["canonical_task_reward_total"]) == float(candidate_100["canonical_task_reward_total"]),
        "canonical_completion_rate_static_across_budget": int(candidate_50["completed_task_count"]) == int(candidate_100["completed_task_count"]),
        "canonical_drop_rate_static_across_budget": int(candidate_50["dropped_task_count"]) == int(candidate_100["dropped_task_count"]),
        "evaluation_action_distribution_static_across_budget": candidate_50["action_distribution"] == candidate_100["action_distribution"],
        "policy_affects_reward": "true" if not reward_same_across_policies else "false",
        "policy_affects_terminal_outcomes": "true" if not terminal_same_across_policies else "false",
        "policy_affects_reward_boolean": not reward_same_across_policies,
        "policy_affects_terminal_outcomes_boolean": not terminal_same_across_policies,
        "candidate_action_distribution_changed_by_budget": candidate_50["action_distribution"] != candidate_100["action_distribution"],
        "candidate_terminal_outcomes_changed_by_budget": (
            candidate_50["completed_task_count"],
            candidate_50["dropped_task_count"],
            candidate_50["pending_task_count"],
        )
        != (
            candidate_100["completed_task_count"],
            candidate_100["dropped_task_count"],
            candidate_100["pending_task_count"],
        ),
        "candidate_policy_vertical_collapse_in_evaluation": float(candidate_100["action_distribution"].get("vertical", 0)) / max(
            sum(candidate_100["action_distribution"].values()), 1
        )
        >= 0.95,
        "candidate_policy_vertical_collapse_in_training_replay_window": candidate_100_replay,
        "policy_results": policy_results,
        "policy_summaries": policy_summaries,
        "fixed_policy_summaries": fixed_policy_summaries,
        "candidate_policy_at_50": candidate_50,
        "candidate_policy_at_100": candidate_100,
        "any_fixed_policy_completes": any_fixed_policy_completes,
    }
