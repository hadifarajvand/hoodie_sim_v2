from __future__ import annotations

from src.analysis.calibration_metric_consistency_reconciliation_fix import action_diversity, reconciliation, runner
from src.analysis.calibration_metric_consistency_reconciliation_fix.universe import build_metric_universe_definitions
from src.analysis.completion_path_deadline_feasibility_repair import feasibility as base_feasibility

from tests.unit.test_calibration_metric_consistency_reconciliation_fix_schema import (
    fake_estimate_task_action_feasibility,
    make_synthetic_raw_report,
)


def test_metric_universe_definitions_and_compatible_counts(monkeypatch):
    monkeypatch.setattr(runner, "load_feature_069_raw_report", lambda config=None: make_synthetic_raw_report())
    monkeypatch.setattr(runner, "generate_figures", lambda payload, figures_dir: [])
    monkeypatch.setattr(runner, "git_status_paths", lambda: ["src/analysis/calibration_metric_consistency_reconciliation_fix/runner.py"])
    monkeypatch.setattr(runner, "git_staged_paths", lambda: [])
    monkeypatch.setattr(runner, "git_diff_paths", lambda base_ref: ["src/analysis/calibration_metric_consistency_reconciliation_fix/runner.py"])
    monkeypatch.setattr(reconciliation, "estimate_task_action_feasibility", fake_estimate_task_action_feasibility)
    monkeypatch.setattr(action_diversity, "estimate_task_action_feasibility", fake_estimate_task_action_feasibility)
    monkeypatch.setattr(base_feasibility, "estimate_task_action_feasibility", fake_estimate_task_action_feasibility)

    report = runner.build_calibration_metric_consistency_reconciliation_report()
    universes = build_metric_universe_definitions()
    assert report["metric_universe_definitions"]["u_unique_tasks"]["name"] == universes["u_unique_tasks"]["name"]
    candidate_50 = report["consistent_policy_effect_comparison"]["policy_summaries"]["candidate_policy_at_50"]
    assert candidate_50["feasible_task_count_universe"] == "U_selected_action_tasks"
    assert candidate_50["completed_feasible_task_count_universe"] == "U_selected_action_tasks"
    assert candidate_50["feasible_task_count"] == candidate_50["selected_action_feasible_task_count"]
    assert candidate_50["completed_feasible_task_count"] == candidate_50["completed_selected_action_feasible_count"]
    assert candidate_50["selected_action_feasible_task_count"] + candidate_50["selected_action_infeasible_task_count"] == candidate_50["unique_task_count"]
