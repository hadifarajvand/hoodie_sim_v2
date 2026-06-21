from __future__ import annotations

from src.analysis.state_representation_deadline_queue_feasibility_repair.comparison import (
    build_action_collapse_diagnostics,
    build_reconciliation_after_state_repair,
    build_selected_action_feasibility_diagnostics,
    build_state_profile_50_100_comparison,
)
from tests.unit.test_state_representation_deadline_queue_feasibility_repair_schema import make_policy_effect, make_policy_summary


def test_action_collapse_and_feasibility_diagnostics_are_computed() -> None:
    legacy_100 = make_policy_summary(
        policy_name="candidate_policy_at_100",
        checkpoint_budget=100,
        action_distribution={"local": 1, "horizontal": 0, "vertical": 99},
        selected_action_feasible_task_count=6,
        selected_action_infeasible_task_count=94,
        completed_count=10,
        dropped_count=85,
        pending_count=5,
        mean_reward=-11.0,
        reward_per_task=-11.0,
        reward_per_decision=-11.0,
        dominant_action_share=0.99,
    )
    new_100 = make_policy_summary(
        policy_name="candidate_policy_at_100",
        checkpoint_budget=100,
        action_distribution={"local": 20, "horizontal": 10, "vertical": 70},
        selected_action_feasible_task_count=18,
        selected_action_infeasible_task_count=82,
        completed_count=18,
        dropped_count=72,
        pending_count=10,
        mean_reward=-8.0,
        reward_per_task=-8.0,
        reward_per_decision=-8.0,
        dominant_action_share=0.70,
    )
    collapse = build_action_collapse_diagnostics(legacy_100, new_100)
    feasibility = build_selected_action_feasibility_diagnostics(legacy_100, new_100)
    assert collapse["action_collapse_reduced"] is True
    assert collapse["legacy_state_dim"] == 3
    assert collapse["new_state_dim"] == 30
    assert feasibility["selected_action_feasible_ratio_delta"] > 0
    assert feasibility["completed_selected_action_feasible_delta"] > 0


def test_state_profile_50_100_comparison_classifies_new_profile_changes() -> None:
    comparison = build_state_profile_50_100_comparison(make_policy_effect()["policy_summaries"])
    assert comparison["checkpoint_budgets"] == [50, 100]
    assert comparison["comparison_classification"] == "completion_path_changed"
    assert comparison["comparison"]["50_to_100_action_distribution_changed"] is True
    reconciliation = build_reconciliation_after_state_repair(make_policy_effect()["policy_summaries"])
    assert reconciliation["reward_reconciliation_passed"] is True
    assert reconciliation["terminal_reconciliation_passed"] is True
    assert reconciliation["raw_vs_canonical_reward_delta_max"] == 0.0

