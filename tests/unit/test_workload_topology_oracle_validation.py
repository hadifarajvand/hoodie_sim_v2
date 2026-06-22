"""Unit tests: workload/topology oracle-validation policy logic and artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.analysis.paper_faithful_simulation_production import oracle_validation as ov


def test_mixed_policy_helpers_respect_legality():
    split = ov._capacity_proportional_split(__import__("random").Random(0))
    oracle = ov._slack_feasibility_oracle()
    mask = {"local": True, "horizontal": False, "vertical": True}

    class _T:
        def dim(self):
            return 1

        def tolist(self):
            # 30-d state vector; mark vertical feasible, local infeasible.
            row = [0.0] * 30
            row[ov.IDX_FEASIBLE["vertical"]] = 1.0
            row[ov.IDX_TOTAL["vertical"]] = 0.1
            row[ov.IDX_TOTAL["local"]] = 0.9
            return row

    # split only ever returns a legal action
    for _ in range(20):
        assert split(_T(), mask, {}) in ("local", "vertical")
    # oracle prefers the feasible legal action (vertical here) over infeasible local
    assert oracle(_T(), mask, {}) == "vertical"


def test_capacity_weights_match_pool_capacity_ratio():
    # private 10 : public 10 : cloud 3 (Gcycle/slot system-wide).
    assert ov._CAP_WEIGHTS == {"local": 10.0, "horizontal": 10.0, "vertical": 3.0}


def test_episode_bound_enforced(monkeypatch):
    # CLI must reject >1000 episodes (no 5000).
    import sys

    monkeypatch.setattr(sys, "argv", ["oracle", "--episodes", "5000"])
    with pytest.raises(ValueError):
        ov.main()


ROOT = ov.OUT_DIR
pytestmark_skip = not (ROOT / "oracle-validation-report.json").exists()


@pytest.mark.skipif(pytestmark_skip, reason="oracle validation artifacts not present; run it first")
def test_report_artifact_is_consistent():
    rep = json.loads((ROOT / "oracle-validation-report.json").read_text())
    assert rep["training_run"] is False
    assert rep["training_5000_run"] is False
    assert rep["algorithm_changed"] is False
    assert rep["parameters_changed"] is False
    assert rep["verdict"] in (
        "no_mixed_policy_outperforms_fixed_local",
        "mixed_policy_outperforms_fixed_local",
    )
    # fixed_local completion must be in the expected calibrated range (~0.25).
    assert 0.15 <= rep["policy_results"]["fixed_local"]["completion_ratio"] <= 0.40
    assert rep["reconciliation_all_pass"] is True
    assert Path(ROOT / "figures" / "figure_01_oracle_policy_comparison.png").exists()
