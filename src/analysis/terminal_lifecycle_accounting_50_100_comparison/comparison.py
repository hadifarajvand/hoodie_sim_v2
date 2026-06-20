from __future__ import annotations

from typing import Any

from .reconciliation import build_checkpoint_comparison


def build_budget_comparison(checkpoint_results: list[dict[str, Any]], policy_effect: dict[str, Any]) -> dict[str, Any]:
    checkpoint_comparison = build_checkpoint_comparison(checkpoint_results)
    candidate_50 = policy_effect["policy_results"].get("candidate_policy_at_50", {})
    candidate_100 = policy_effect["policy_results"].get("candidate_policy_at_100", {})
    comparison = dict(checkpoint_comparison.get("comparison", {}))
    comparison.update(
        {
            "candidate_50_action_distribution": candidate_50.get("evaluation_action_distribution", {}),
            "candidate_100_action_distribution": candidate_100.get("evaluation_action_distribution", {}),
            "candidate_action_distribution_changed_by_budget": candidate_50.get("evaluation_action_distribution", {})
            != candidate_100.get("evaluation_action_distribution", {}),
            "candidate_50_completion_count": candidate_50.get("evaluation_reward_summary", {}).get("completed_task_count", 0),
            "candidate_100_completion_count": candidate_100.get("evaluation_reward_summary", {}).get("completed_task_count", 0),
            "candidate_50_drop_count": candidate_50.get("evaluation_reward_summary", {}).get("dropped_task_count", 0),
            "candidate_100_drop_count": candidate_100.get("evaluation_reward_summary", {}).get("dropped_task_count", 0),
            "candidate_50_mean_reward": candidate_50.get("evaluation_reward_summary", {}).get("mean_reward", 0.0),
            "candidate_100_mean_reward": candidate_100.get("evaluation_reward_summary", {}).get("mean_reward", 0.0),
            "candidate_50_terminal_event_coverage_ratio": candidate_50.get("raw_vs_canonical_terminal_reconciliation", {}).get("terminal_event_coverage_ratio", 0.0),
            "candidate_100_terminal_event_coverage_ratio": candidate_100.get("raw_vs_canonical_terminal_reconciliation", {}).get("terminal_event_coverage_ratio", 0.0),
            "candidate_50_reward_event_coverage_ratio": candidate_50.get("raw_vs_canonical_terminal_reconciliation", {}).get("reward_event_coverage_ratio", 0.0),
            "candidate_100_reward_event_coverage_ratio": candidate_100.get("raw_vs_canonical_terminal_reconciliation", {}).get("reward_event_coverage_ratio", 0.0),
            "candidate_50_raw_vs_canonical_reward_delta": candidate_50.get("reward_reconciliation_after_terminal_repair", {}).get("raw_vs_canonical_reward_delta", 0.0),
            "candidate_100_raw_vs_canonical_reward_delta": candidate_100.get("reward_reconciliation_after_terminal_repair", {}).get("raw_vs_canonical_reward_delta", 0.0),
        }
    )
    return {
        "checkpoint_comparison": checkpoint_comparison,
        "comparison": comparison,
        "policy_effect_summary": {
            "candidate_policy_vertical_collapse_in_evaluation": policy_effect.get("candidate_policy_vertical_collapse_in_evaluation", False),
            "candidate_policy_vertical_collapse_in_training_replay_window": policy_effect.get("candidate_policy_vertical_collapse_in_training_replay_window", False),
            "policy_affects_reward": policy_effect.get("policy_affects_reward", "uncertain"),
            "policy_affects_terminal_outcomes": policy_effect.get("policy_affects_terminal_outcomes", "uncertain"),
            "evaluation_reward_static_after_terminal_repair": policy_effect.get("evaluation_reward_static_after_terminal_repair", False),
            "evaluation_action_distribution_static_across_budget": policy_effect.get("evaluation_action_distribution_static_across_budget", False),
        },
    }
