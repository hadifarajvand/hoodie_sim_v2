from __future__ import annotations

from src.analysis.calibration_metric_consistency_reconciliation_fix import action_diversity, reconciliation, runner
from src.analysis.completion_path_deadline_feasibility_repair import feasibility as base_feasibility

from tests.unit.test_calibration_metric_consistency_reconciliation_fix_schema import (
    fake_estimate_task_action_feasibility,
    make_synthetic_raw_report,
)


def test_claim_safety_blocks_superiority_and_reproduction_claims(monkeypatch):
    monkeypatch.setattr(runner, "load_feature_069_raw_report", lambda config=None: make_synthetic_raw_report())
    monkeypatch.setattr(runner, "generate_figures", lambda payload, figures_dir: [])
    monkeypatch.setattr(runner, "git_status_paths", lambda: ["src/analysis/calibration_metric_consistency_reconciliation_fix/runner.py"])
    monkeypatch.setattr(runner, "git_staged_paths", lambda: [])
    monkeypatch.setattr(runner, "git_diff_paths", lambda base_ref: ["src/analysis/calibration_metric_consistency_reconciliation_fix/runner.py"])
    monkeypatch.setattr(reconciliation, "estimate_task_action_feasibility", fake_estimate_task_action_feasibility)
    monkeypatch.setattr(action_diversity, "estimate_task_action_feasibility", fake_estimate_task_action_feasibility)
    monkeypatch.setattr(base_feasibility, "estimate_task_action_feasibility", fake_estimate_task_action_feasibility)

    report = runner.build_calibration_metric_consistency_reconciliation_report()
    assert report["paper_reproduction_claim_made"] is False
    assert report["performance_superiority_claim_made"] is False
    assert report["baseline_superiority_claim_made"] is False
    assert report["claim_safety_status"]["claim_safety_passed"] is True
    assert report["diagnostic_decision"]["recommended_next_action"] == "safe_to_proceed_to_state_representation_repair"
