from __future__ import annotations

from src.analysis.calibration_metric_consistency_reconciliation_fix import action_diversity
from src.analysis.completion_path_deadline_feasibility_repair import feasibility as base_feasibility

from tests.unit.test_calibration_metric_consistency_reconciliation_fix_schema import fake_estimate_task_action_feasibility, make_policy_result


def test_action_diversity_uses_count_and_set_checks(monkeypatch):
    monkeypatch.setattr(action_diversity, "estimate_task_action_feasibility", fake_estimate_task_action_feasibility)
    monkeypatch.setattr(base_feasibility, "estimate_task_action_feasibility", fake_estimate_task_action_feasibility)
    task_records = make_policy_result("candidate_policy_at_100", 100, ["local", "local", "vertical"])["task_records"]
    diversity = action_diversity.build_action_path_diversity(task_records, checkpoint_budget=100)
    assert diversity["count_based_action_feasibility_diversity"] is True
    assert diversity["set_based_action_feasibility_diversity"] is True
    assert diversity["actions_have_different_feasibility"] is True
    assert diversity["feasible_task_count_by_action"]["local"] != diversity["feasible_task_count_by_action"]["horizontal"]
