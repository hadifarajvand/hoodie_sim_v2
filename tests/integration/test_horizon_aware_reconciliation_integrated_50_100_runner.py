"""Integration tests: Feature 081 integrated campaign artifacts and gates.

These tests read the artifacts produced by the integrated 50/100 campaign run
(``python -m src.analysis.paper_faithful_simulation_production_pipeline.runner
--integrated-horizon-aware-rerun``). They are skipped if the campaign has not
been run yet (the campaign is compute-heavy and run once).
"""

from __future__ import annotations

import json

import pytest

from src.analysis.paper_faithful_simulation_production_pipeline.integrated_horizon_rerun import ROOT
from src.analysis.paper_faithful_simulation_production_pipeline.schema import (
    PAPER_COMPATIBLE_METRIC_FIELDS,
)

REPORT = ROOT / "horizon-aware-reconciliation-integrated-report.json"
pytestmark = pytest.mark.skipif(
    not REPORT.exists(), reason="integrated 50/100 campaign artifacts not present; run the campaign first"
)


def _load(name):
    return json.loads((ROOT / name).read_text())


def test_required_artifacts_exist():
    for name in (
        "horizon-aware-reconciliation-integrated-report.json",
        "horizon-aware-reconciliation-integrated-report.md",
        "integrated-50-100-run-manifest.json",
        "integrated-policy-metrics-50.json",
        "integrated-policy-metrics-100.json",
        "integrated-reward-terminal-reconciliation.json",
        "horizon-finalized-task-accounting.json",
        "recovered-reward-event-ledger.json",
        "terminal-event-coverage-report.json",
        "paper-compatible-metric-schema-integrated.json",
        "baseline-policy-validation-integrated.json",
        "candidate-policy-validation-integrated.json",
        "readiness-gates-integrated.json",
        "diagnostic-decision.json",
        "final-integrated-reconciliation-summary.md",
        "figure-manifest.json",
    ):
        assert (ROOT / name).exists(), name


def test_reward_and_terminal_reconciliation_passed():
    report = _load("horizon-aware-reconciliation-integrated-report.json")
    assert report["campaign_level_reward_reconciliation_passed"] is True
    assert report["campaign_level_terminal_reconciliation_passed"] is True
    assert abs(report["raw_vs_canonical_reward_delta_max"]) <= 1e-9
    assert abs(report["terminal_event_coverage_ratio_min"] - 1.0) <= 1e-9


def test_all_policies_reconciled():
    for budget in (50, 100):
        rows = _load(f"integrated-policy-metrics-{budget}.json")
        assert rows
        for row in rows:
            assert set(row) == set(PAPER_COMPATIBLE_METRIC_FIELDS)
            assert row["reward_reconciled"] is True
            assert row["terminal_reconciled"] is True
            assert abs(row["raw_vs_canonical_reward_delta"]) <= 1e-9


def test_completion_nonzero_and_fixed_baselines_valid():
    report = _load("horizon-aware-reconciliation-integrated-report.json")
    assert report["completion_count_nonzero"] is True
    assert report["fixed_policy_completion_present"] is True


def test_recovered_reward_event_counts_reported():
    detail = _load("integrated-reward-terminal-reconciliation.json")
    for per in detail["per_policy"]:
        assert "recovered_horizon_reward_event_count" in per
        assert per["raw_plus_recovered_reward_total"] == per["canonical_reward_total"]


def test_fourteen_gates_pass():
    gates = _load("readiness-gates-integrated.json")
    assert gates["gates_passed"] == 14
    assert gates["all_pass"] is True


def test_claim_safety_false():
    report = _load("horizon-aware-reconciliation-integrated-report.json")
    cs = report["claim_safety"]
    assert cs["paper_reproduction_claim_made"] is False
    assert cs["exact_numerical_reproduction_claim_made"] is False
    assert cs["performance_superiority_claim_made"] is False
    assert cs["baseline_superiority_claim_made"] is False
    assert cs["training_5000_run"] is False
    assert cs["max_training_budget_executed"] == 100
