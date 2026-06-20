from __future__ import annotations

import json

from src.analysis.calibration_metric_consistency_reconciliation_fix import action_diversity, reconciliation, runner
from src.analysis.calibration_metric_consistency_reconciliation_fix.report import write_calibration_metric_consistency_report
from src.analysis.completion_path_deadline_feasibility_repair import feasibility as base_feasibility

from tests.unit.test_calibration_metric_consistency_reconciliation_fix_schema import (
    fake_estimate_task_action_feasibility,
    make_synthetic_raw_report,
)


def test_report_includes_consistent_policy_metrics(tmp_path, monkeypatch):
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
    payload = json.loads((tmp_path / "calibration-metric-consistency-report.json").read_text())

    candidate_50 = payload["consistent_policy_effect_comparison"]["policy_summaries"]["candidate_policy_at_50"]
    candidate_100 = payload["consistent_policy_effect_comparison"]["policy_summaries"]["candidate_policy_at_100"]
    assert candidate_50["reward_reconciliation_status"] == "passed"
    assert candidate_100["reward_reconciliation_status"] == "passed"
    assert candidate_50["feasible_task_count_universe"] == "U_selected_action_tasks"
    assert candidate_100["completed_feasible_task_count_universe"] == "U_selected_action_tasks"
    assert payload["reward_terminal_reconciliation_fix"]["reward_reconciliation_status"] == "passed"
    assert payload["action_path_diversity_check"]["actions_have_different_feasibility"] is True
