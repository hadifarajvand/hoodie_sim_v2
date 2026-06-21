"""Integration tests: production pipeline artifacts and readiness gates.

Reads artifacts produced by:
    python -m src.analysis.paper_faithful_simulation_production.runner --medium-smoke
Skipped if the medium smoke has not been run (it is compute-heavy, run once).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.analysis.paper_faithful_simulation_production.metric_schema import (
    PAPER_COMPATIBLE_METRIC_FIELDS,
)

ROOT = Path("artifacts/production/paper-faithful-simulation")
REPORT = ROOT / "final-production-simulation-report.json"
pytestmark = pytest.mark.skipif(
    not (ROOT / "medium-smoke-candidate-metrics.json").exists()
    or not json.loads((ROOT / "production-run-manifest.json").read_text()).get("training_budgets_executed"),
    reason="medium smoke artifacts not present; run the smoke first",
)


def _load(name):
    return json.loads((ROOT / name).read_text())


def test_required_artifacts_exist():
    for name in (
        "mechanism-map.json", "mechanism-map.md", "paper-source-audit.json",
        "implementation-plan.json", "implementation-plan.md", "production-run-manifest.json",
        "medium-smoke-config.json", "medium-smoke-candidate-metrics.json",
        "medium-smoke-baseline-metrics.json", "paper-compatible-metric-schema.json",
        "reward-terminal-reconciliation-report.json", "state-profile-consistency-report.json",
        "readiness-gates.json", "claim-safety.json", "final-production-simulation-report.json",
        "final-production-simulation-report.md", "commit-summary.md", "figure-manifest.json",
    ):
        assert (ROOT / name).exists(), name


def test_all_figures_exist():
    for i in range(1, 9):
        assert list((ROOT / "figures").glob(f"figure_{i:02d}_*.png")), f"figure {i:02d} missing"


def test_sixteen_gates_pass():
    gates = _load("readiness-gates.json")
    assert gates["all_pass"] is True
    assert gates["gates_passed"] == len(gates["gates"])


def test_reconciliation_passed_for_all_policies():
    for name in ("medium-smoke-candidate-metrics.json", "medium-smoke-baseline-metrics.json"):
        rows = _load(name)
        assert rows
        for r in rows:
            assert set(r) == set(PAPER_COMPATIBLE_METRIC_FIELDS)
            assert r["reward_reconciled"] is True
            assert r["terminal_reconciled"] is True
            assert abs(r["raw_vs_canonical_reward_delta"]) <= 1e-9


def test_candidate_budgets_50_100_200_300():
    rows = _load("medium-smoke-candidate-metrics.json")
    budgets = sorted(r["training_budget"] for r in rows)
    assert budgets == [50, 100, 200, 300]


def test_completion_nonzero_and_drop_pressure():
    report = _load("final-production-simulation-report.json")
    assert report["completion_nonzero"] is True
    gates = _load("readiness-gates.json")["gates"]
    assert gates["drop_or_deadline_pressure_active"] is True


def test_claim_safety_false_and_no_5000():
    cs = _load("claim-safety.json")
    assert cs["paper_reproduction_claim_made"] is False
    assert cs["performance_superiority_claim_made"] is False
    assert cs["baseline_superiority_claim_made"] is False
    assert cs["training_5000_run"] is False
    assert cs["max_training_budget_executed"] == 300


def test_energy_metric_status_documented():
    schema = _load("paper-compatible-metric-schema.json")
    assert schema["energy_metric_status"] == "not_implemented"
