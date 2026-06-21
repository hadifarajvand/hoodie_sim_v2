"""Unit tests: extended-smoke profile and stability report (no 5000)."""

from __future__ import annotations

import pytest

from src.analysis.paper_faithful_simulation_production import profiles
from src.analysis.paper_faithful_simulation_production.runner import _stability_report


def test_extended_profile_budgets():
    p = profiles.extended_smoke_profile()
    assert p.training_budgets == [300, 500, 750, 1000]
    assert p.max_training_budget == 1000
    assert 5000 not in p.training_budgets
    assert p.episode_length == 110


def test_budget_above_ceiling_rejected():
    with pytest.raises(ValueError):
        profiles.ProductionProfile(training_budgets=[300, 2000], max_training_budget=2000)
    with pytest.raises(ValueError):
        profiles.ProductionProfile(training_budgets=[300, 5000], max_training_budget=1000)


def _row(budget, completion, drop, reward, recon=True, actions=(4000, 3000, 3000), policy_name="fixed_local_policy"):
    return {
        "training_budget": budget, "completion_ratio": completion, "drop_ratio": drop,
        "reward_per_task": reward, "reward_reconciled": recon, "terminal_reconciled": recon,
        "action_local_count": actions[0], "action_horizontal_count": actions[1],
        "action_vertical_count": actions[2], "policy_name": policy_name,
    }


def test_stability_report_detects_plateau_and_no_regression():
    cand = [_row(300, 0.25, 0.66, -28.0), _row(500, 0.25, 0.66, -28.0),
            _row(750, 0.25, 0.66, -28.0), _row(1000, 0.25, 0.66, -28.0)]
    base = [_row(None, 0.246, 0.66, -29.0)]
    rep = _stability_report(cand, base)
    assert rep["all_policies_reconciled"] is True
    assert rep["completion_nonzero_all_budgets"] is True
    assert rep["no_late_completion_regression"] is True
    assert rep["converged_plateau_detected"] is True
    assert rep["stability_passed"] is True


def test_stability_report_flags_late_regression():
    cand = [_row(300, 0.30, 0.6, -20.0), _row(500, 0.30, 0.6, -20.0),
            _row(750, 0.30, 0.6, -20.0), _row(1000, 0.10, 0.8, -40.0)]
    rep = _stability_report(cand, [])
    assert rep["no_late_completion_regression"] is False
    assert rep["stability_passed"] is False


def test_stability_report_flags_unreconciled():
    cand = [_row(300, 0.25, 0.66, -28.0, recon=False), _row(500, 0.25, 0.66, -28.0)]
    rep = _stability_report(cand, [])
    assert rep["all_policies_reconciled"] is False
    assert rep["stability_passed"] is False


def test_stability_report_detects_action_collapse_and_no_progress():
    # Candidate collapsed to 100% local at every budget, identical across budgets.
    collapsed = (10412, 0, 0)
    cand = [_row(b, 0.246, 0.663, -28.99, actions=collapsed) for b in (300, 500, 750, 1000)]
    base = [_row(None, 0.246, 0.663, -28.99, actions=collapsed)]
    rep = _stability_report(cand, base)
    lh = rep["learning_health"]
    assert lh["candidate_action_collapse_detected"] is True
    assert lh["no_learning_progress_detected"] is True
    assert lh["candidate_action_signature_matches_baseline"] is not None
    assert lh["learning_health_ok"] is False
    # Pipeline-stability still passes (reconciled, nonzero, no regression).
    assert rep["stability_passed"] is True


def test_stability_report_healthy_when_diverse_and_improving():
    cand = [
        _row(300, 0.20, 0.70, -32.0, actions=(5000, 3000, 2412)),
        _row(1000, 0.30, 0.60, -24.0, actions=(4000, 3500, 2912)),
    ]
    rep = _stability_report(cand, [])
    lh = rep["learning_health"]
    assert lh["candidate_action_collapse_detected"] is False
    assert lh["no_learning_progress_detected"] is False
    assert lh["learning_health_ok"] is True
