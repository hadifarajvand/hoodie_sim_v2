from __future__ import annotations

from src.analysis.deadline_timeout_feasible_workload_calibration.diagnostics import (
    FORBIDDEN_PREFIXES,
    FEATURE_SCOPE_PREFIXES,
    build_scope_guard_summary,
)


def test_scope_guard_detects_forbidden_paths_and_ignores_noise():
    summary = build_scope_guard_summary(
        status_paths=[
            "src/analysis/deadline_timeout_feasible_workload_calibration/config.py",
            "notes/unrelated.txt",
            "src/environment/reward_timing.py",
        ],
        staged_paths=["src/analysis/deadline_timeout_feasible_workload_calibration/runner.py"],
        diff_paths=["src/analysis/deadline_timeout_feasible_workload_calibration/report.py"],
        approved_prefixes=FEATURE_SCOPE_PREFIXES,
        forbidden_prefixes=FORBIDDEN_PREFIXES,
    )

    assert summary["working_tree_paths_approved"] is False
    assert summary["staged_paths_approved"] is True
    assert summary["base_branch_head_diff_approved"] is True
    assert "src/environment/reward_timing.py" in summary["forbidden_paths_detected"]
