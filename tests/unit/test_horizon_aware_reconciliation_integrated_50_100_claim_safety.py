"""Unit tests: claim-safety and budget guards for Feature 081."""

from __future__ import annotations

from src.analysis.paper_faithful_simulation_production_pipeline import integrated_horizon_rerun as ihr


def test_budgets_are_only_50_100():
    assert ihr.TRAINING_BUDGETS == [50, 100]
    assert ihr.MAX_TRAINING_BUDGET == 100
    for forbidden in (150, 200, 500, 1000, 2000, 5000):
        assert forbidden not in ihr.TRAINING_BUDGETS


def test_evaluation_config_constants():
    assert ihr.EVALUATION_EPISODE_COUNT == 100
    assert ihr.EPISODE_LENGTH == 110
    assert ihr.CALIBRATION_PROFILE == "paper_aligned_feasible_v1"


def test_no_forbidden_budget_executed():
    # The training_5000_run flag must stay false and 5000 must never be a budget.
    assert 5000 not in ihr.TRAINING_BUDGETS
    assert ihr.MAX_TRAINING_BUDGET < 150
