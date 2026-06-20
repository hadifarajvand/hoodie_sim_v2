from __future__ import annotations

import json
from pathlib import Path

from src.analysis.calibration_metric_consistency_reconciliation_fix import action_diversity, reconciliation, runner
from src.analysis.calibration_metric_consistency_reconciliation_fix.report import write_calibration_metric_consistency_report
from src.analysis.completion_path_deadline_feasibility_repair import feasibility as base_feasibility

from tests.unit.test_calibration_metric_consistency_reconciliation_fix_schema import (
    fake_estimate_task_action_feasibility,
    make_synthetic_raw_report,
)


def test_integration_generates_required_artifacts(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "load_feature_069_raw_report", lambda config=None: make_synthetic_raw_report())
    monkeypatch.setattr(runner, "git_status_paths", lambda: ["src/analysis/calibration_metric_consistency_reconciliation_fix/runner.py"])
    monkeypatch.setattr(runner, "git_staged_paths", lambda: [])
    monkeypatch.setattr(runner, "git_diff_paths", lambda base_ref: ["src/analysis/calibration_metric_consistency_reconciliation_fix/runner.py"])
    monkeypatch.setattr(reconciliation, "estimate_task_action_feasibility", fake_estimate_task_action_feasibility)
    monkeypatch.setattr(action_diversity, "estimate_task_action_feasibility", fake_estimate_task_action_feasibility)
    monkeypatch.setattr(base_feasibility, "estimate_task_action_feasibility", fake_estimate_task_action_feasibility)
    monkeypatch.setattr(runner, "FIGURES_DIR", tmp_path / "figures")

    report = runner.build_calibration_metric_consistency_reconciliation_report()
    write_calibration_metric_consistency_report(report, tmp_path)

    required = [
        "calibration-metric-consistency-report.json",
        "calibration-metric-consistency-report.md",
        "metric-universe-definitions.json",
        "policy-metric-consistency-checks.json",
        "reward-terminal-reconciliation-fix.json",
        "action-path-diversity-check.json",
        "consistent-policy-effect-comparison.json",
        "consistent-50-100-comparison.json",
        "before-after-consistency-comparison.json",
        "diagnostic-decision.json",
        "final-consistency-summary.md",
        "figure-manifest.json",
    ]
    for name in required:
        assert (tmp_path / name).exists(), name
    assert len(list((tmp_path / "figures").glob("*.png"))) == 5
    payload = json.loads((tmp_path / "calibration-metric-consistency-report.json").read_text())
    assert payload["final_verdict"] == "calibration_metric_consistency_reconciliation_ready"
    assert payload["figure_manifest"]["figure_count"] == 5
