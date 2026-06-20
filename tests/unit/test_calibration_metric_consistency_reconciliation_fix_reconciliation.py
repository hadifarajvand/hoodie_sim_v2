from __future__ import annotations

from src.analysis.calibration_metric_consistency_reconciliation_fix import action_diversity, reconciliation, runner
from src.analysis.completion_path_deadline_feasibility_repair import feasibility as base_feasibility

from tests.unit.test_calibration_metric_consistency_reconciliation_fix_schema import (
    fake_estimate_task_action_feasibility,
    make_synthetic_raw_report,
)


def test_reward_terminal_reconciliation_and_policy_consistency(monkeypatch):
    monkeypatch.setattr(runner, "load_feature_069_raw_report", lambda config=None: make_synthetic_raw_report())
    monkeypatch.setattr(runner, "generate_figures", lambda payload, figures_dir: [])
    monkeypatch.setattr(runner, "git_status_paths", lambda: ["src/analysis/calibration_metric_consistency_reconciliation_fix/runner.py"])
    monkeypatch.setattr(runner, "git_staged_paths", lambda: [])
    monkeypatch.setattr(runner, "git_diff_paths", lambda base_ref: ["src/analysis/calibration_metric_consistency_reconciliation_fix/runner.py"])
    monkeypatch.setattr(reconciliation, "estimate_task_action_feasibility", fake_estimate_task_action_feasibility)
    monkeypatch.setattr(action_diversity, "estimate_task_action_feasibility", fake_estimate_task_action_feasibility)
    monkeypatch.setattr(base_feasibility, "estimate_task_action_feasibility", fake_estimate_task_action_feasibility)

    report = runner.build_calibration_metric_consistency_reconciliation_report()
    fix = report["reward_terminal_reconciliation_fix"]
    assert fix["reward_reconciled"] is True
    assert fix["terminal_reconciled"] is True
    assert fix["reward_reconciliation_status"] == "passed"
    assert fix["max_raw_vs_canonical_reward_delta"] == 0.0
    candidate_100 = report["consistent_policy_effect_comparison"]["policy_summaries"]["candidate_policy_at_100"]
    assert candidate_100["reward_reconciliation_status"] == "passed"
    assert candidate_100["terminal_reconciled"] is True
    assert candidate_100["reward_reconciled"] is True
    assert candidate_100["raw_event_reward_count"] == candidate_100["canonical_task_reward_count"]
    assert candidate_100["raw_terminal_event_count"] == candidate_100["canonical_terminal_task_count"]
    assert candidate_100["raw_vs_canonical_reward_delta"] == 0.0
