"""Integration tests: training-stability repair artifacts and gates.

Reads artifacts produced by:
    python -m src.analysis.paper_faithful_simulation_production.runner --training-stability-repair
Skipped if the repair smoke has not been run (compute-heavy; run once).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.analysis.paper_faithful_simulation_production.metric_schema import (
    PAPER_COMPATIBLE_METRIC_FIELDS,
)

ROOT = Path("artifacts/production/training-stability-exploration-repair")
pytestmark = pytest.mark.skipif(
    not (ROOT / "final-training-stability-report.json").exists(),
    reason="training-stability repair artifacts not present; run the repair smoke first",
)


def _load(name):
    return json.loads((ROOT / name).read_text())


def test_required_artifacts_exist():
    for name in (
        "training-failure-audit.json", "training-failure-audit.md", "repair-plan.json", "repair-plan.md",
        "paper-training-parameter-audit.json", "epsilon-schedule-audit.json", "replay-action-balance-audit.json",
        "q-value-diagnostics.json", "target-update-double-dqn-audit.json", "dueling-architecture-audit.json",
        "loss-gradient-diagnostics.json", "training-health-report.json",
        "repaired-medium-smoke-candidate-metrics.json", "repaired-medium-smoke-baseline-metrics.json",
        "reward-terminal-reconciliation-report.json", "readiness-gates.json", "claim-safety.json",
        "final-training-stability-report.json", "final-training-stability-report.md", "commit-summary.md",
    ):
        assert (ROOT / name).exists(), name


def test_all_seven_figures_exist():
    for i in range(1, 8):
        assert list((ROOT / "figures").glob(f"figure_{i:02d}_*.png")), f"figure {i:02d} missing"


def test_reconciliation_still_passes():
    rep = _load("final-training-stability-report.json")
    pg = rep["pipeline_gates"]
    assert pg["reward_reconciliation_passed"] is True
    assert pg["terminal_reconciliation_passed"] is True
    assert abs(rep["raw_vs_canonical_reward_delta_max"]) <= 1e-9
    assert abs(rep["terminal_event_coverage_ratio_min"] - 1.0) <= 1e-9


def test_metric_schema_consistent():
    for name in ("repaired-medium-smoke-candidate-metrics.json", "repaired-medium-smoke-baseline-metrics.json"):
        rows = _load(name)
        assert rows
        for r in rows:
            assert set(r) == set(PAPER_COMPATIBLE_METRIC_FIELDS)


def test_exploration_random_ratio_nonzero():
    eps = _load("epsilon-schedule-audit.json")
    assert eps["epsilon_eval"] == 0.0
    assert all(b["random_action_ratio"] > 0 for b in eps["per_budget"])


def test_learning_recovery_signals():
    health = _load("training-health-report.json")
    lg = health["learning_gates"]
    # At least one strong recovery signal must hold.
    assert (
        lg["exploration_random_action_ratio_nonzero_during_training"]
        and (lg["q_values_have_nonzero_action_separation"]
             or lg["completion_or_reward_changes_across_budgets"]
             or lg["candidate_action_collapse_resolved"])
    )


def test_candidate_budgets_50_to_1000():
    rows = _load("repaired-medium-smoke-candidate-metrics.json")
    assert sorted(r["training_budget"] for r in rows) == [50, 100, 200, 300, 500, 750, 1000]


def test_no_5000_and_claim_safety():
    cs = _load("claim-safety.json")
    assert cs["training_5000_run"] is False
    assert cs["max_training_budget_executed"] == 1000
    assert cs["performance_superiority_claim_made"] is False
    assert cs["baseline_superiority_claim_made"] is False
