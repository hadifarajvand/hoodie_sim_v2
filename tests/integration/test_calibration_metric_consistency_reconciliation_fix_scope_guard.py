from __future__ import annotations

from src.analysis.calibration_metric_consistency_reconciliation_fix.diagnostics import APPROVED_PREFIXES, FORBIDDEN_PREFIXES, build_scope_guard_summary, classify_paths


def test_scope_guard_allows_only_approved_feature_paths():
    summary = build_scope_guard_summary(
        ["src/analysis/calibration_metric_consistency_reconciliation_fix/runner.py"],
        [],
        ["src/analysis/calibration_metric_consistency_reconciliation_fix/runner.py"],
        APPROVED_PREFIXES,
        FORBIDDEN_PREFIXES,
    )
    assert summary["working_tree_paths_approved"] is True
    assert summary["staged_paths_approved"] is True
    assert summary["base_branch_head_diff_approved"] is True


def test_scope_guard_detects_forbidden_paths():
    result = classify_paths(
        ["src/environment/environment.py", "src/analysis/calibration_metric_consistency_reconciliation_fix/runner.py"],
        APPROVED_PREFIXES,
        FORBIDDEN_PREFIXES,
    )
    assert result["approved"] is False
    assert "src/environment/environment.py" in result["forbidden_paths_detected"]
