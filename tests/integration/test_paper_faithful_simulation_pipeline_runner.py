"""Integration test for the Feature 080 pipeline runner artifacts and gates."""

from __future__ import annotations

import json
from pathlib import Path

from src.analysis.paper_faithful_simulation_production_pipeline.runner import ROOT, run
from src.analysis.paper_faithful_simulation_production_pipeline.schema import (
    PAPER_COMPATIBLE_METRIC_FIELDS,
)


def test_runner_produces_blocked_verdict_and_artifacts():
    result = run(emit_json=False)
    # Reconciliation is not yet reconciled at campaign level -> blocked.
    assert result["final_verdict"] == "paper_faithful_simulation_pipeline_blocked"
    assert result["recommended_next_diagnostic_decision"] == "fix_reward_terminal_reconciliation_next"
    assert result["gates"]["gate_6_reward_reconciliation_passed"] is False
    assert result["gates"]["gate_7_terminal_reconciliation_passed"] is False
    assert result["claim_safety"]["paper_reproduction_claim_made"] is False
    assert result["claim_safety"]["training_5000_run"] is False
    assert result["claim_safety"]["max_training_budget_executed"] == 0


def test_required_artifacts_exist():
    run(emit_json=False)
    required = [
        "paper-component-alignment-audit.json",
        "paper-component-alignment-audit.md",
        "current-blocker-root-cause-analysis.json",
        "current-blocker-root-cause-analysis.md",
        "implementation-plan.json",
        "implementation-plan.md",
        "pipeline-repair-report.json",
        "pipeline-repair-report.md",
        "reward-terminal-reconciliation-after-repair.json",
        "state-profile-consistency-after-repair.json",
        "metric-universe-consistency-after-repair.json",
        "baseline-policy-validation.json",
        "candidate-policy-validation-50-100.json",
        "production-style-run-manifest.json",
        "paper-compatible-metric-schema.json",
        "paper-compatible-metrics-50.json",
        "paper-compatible-metrics-100.json",
        "figure-manifest.json",
        "diagnostic-decision.json",
        "final-pipeline-readiness-summary.md",
    ]
    for name in required:
        assert (ROOT / name).exists(), name


def test_metric_schema_consistent_across_policies():
    run(emit_json=False)
    for budget in (50, 100):
        rows = json.loads((ROOT / f"paper-compatible-metrics-{budget}.json").read_text())
        assert rows
        for row in rows:
            assert set(row) == set(PAPER_COMPATIBLE_METRIC_FIELDS)


def test_all_seven_figures_exist():
    run(emit_json=False)
    for i in range(1, 8):
        matches = list((ROOT / "figures").glob(f"figure_{i:02d}_*.png"))
        assert matches, f"figure {i:02d} missing"
