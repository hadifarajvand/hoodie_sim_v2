"""Integration tests: reward-signal repair artifacts and gates.

Reads artifacts from:
    python -m src.analysis.paper_faithful_simulation_production.runner --reward-signal-repair
Skipped if the repair smoke has not been run (compute-heavy; run once).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.analysis.paper_faithful_simulation_production.metric_schema import PAPER_COMPATIBLE_METRIC_FIELDS

ROOT = Path("artifacts/production/reward-signal-state-action-discrimination-repair")
pytestmark = pytest.mark.skipif(
    not (ROOT / "final-report.json").exists(),
    reason="reward-signal repair artifacts not present; run the repair smoke first",
)


def _load(name):
    return json.loads((ROOT / name).read_text())


def test_required_artifacts_exist():
    for name in (
        "audit-report.json", "audit-report.md", "paper-reward-equation-audit.json",
        "state-feature-discrimination-audit.json", "per-action-return-audit.json",
        "q-value-state-action-audit.json", "advantage-head-audit.json", "lstm-window-usage-audit.json",
        "td-target-loss-audit.json", "reward-scale-gradient-audit.json", "policy-collapse-root-cause.json",
        "repair-plan.json", "repair-plan.md", "repair-implementation-summary.json",
        "before-after-learning-health.json", "candidate-metrics-after-repair.json",
        "baseline-metrics-after-repair.json", "reward-terminal-reconciliation-after-repair.json",
        "readiness-gates.json", "claim-safety.json", "final-report.json", "final-report.md", "commit-summary.md",
    ):
        assert (ROOT / name).exists(), name


def test_all_seven_figures_exist():
    for i in range(1, 8):
        assert list((ROOT / "figures").glob(f"figure_{i:02d}_*.png")), f"figure {i:02d} missing"


def test_pipeline_reconciliation_still_passes():
    rep = _load("final-report.json")
    pg = rep["pipeline_gates"]
    assert pg["reward_reconciliation_passed"] is True
    assert pg["terminal_reconciliation_passed"] is True
    assert abs(rep["raw_vs_canonical_reward_delta_max"]) <= 1e-9
    assert abs(rep["terminal_event_coverage_ratio_min"] - 1.0) <= 1e-9
    assert pg["metric_schema_valid"] is True
    assert pg["completion_nonzero"] is True


def test_metric_schema_consistent():
    for name in ("candidate-metrics-after-repair.json", "baseline-metrics-after-repair.json"):
        rows = _load(name)
        assert rows
        for r in rows:
            assert set(r) == set(PAPER_COMPATIBLE_METRIC_FIELDS)


def test_raw_reward_not_silently_changed():
    cs = _load("claim-safety.json")
    assert cs["raw_reward_semantics_changed"] is False
    assert cs["training_only_reward_transform"] == "per_task_delayed_reward_credit_assignment"


def test_before_after_and_per_action_separation():
    ba = _load("before-after-learning-health.json")
    assert "before" in ba and "after" in ba
    par = _load("per-action-return-audit.json")
    assert par["per_action_return_separation_detected"] is True
    before = par["before_per_action_mean_reward"]
    after = par["after_per_action_mean_reward"]
    assert max(before.values()) - min(before.values()) < 3.0
    assert max(after.values()) - min(after.values()) > 3.0


def test_at_least_two_learning_signals_met():
    rg = _load("readiness-gates.json")
    assert rg["signals_met"] >= 2


def test_no_5000_and_claim_safety():
    cs = _load("claim-safety.json")
    assert cs["training_5000_run"] is False
    assert cs["max_training_budget_executed"] == 1000
    assert cs["performance_superiority_claim_made"] is False
    assert cs["baseline_superiority_claim_made"] is False
