from __future__ import annotations

from src.analysis.state_representation_deadline_queue_feasibility_repair.diagnostics import (
    FORBIDDEN_PREFIXES,
    APPROVED_PREFIXES,
    build_prerequisite_tags,
    build_scope_guard_summary,
    load_feature_070_status,
)


def test_scope_guard_rejects_forbidden_paths() -> None:
    summary = build_scope_guard_summary(
        ["src/analysis/state_representation_deadline_queue_feasibility_repair/runner.py"],
        ["src/analysis/state_representation_deadline_queue_feasibility_repair/runner.py"],
        ["src/analysis/state_representation_deadline_queue_feasibility_repair/runner.py"],
    )
    assert summary["working_tree_paths_approved"] is True
    assert summary["staged_paths_approved"] is True
    assert summary["base_branch_head_diff_approved"] is True

    forbidden = build_scope_guard_summary(
        ["src/environment/environment.py"],
        ["src/analysis/state_representation_deadline_queue_feasibility_repair/runner.py"],
        ["src/environment/environment.py"],
    )
    assert forbidden["working_tree_paths_approved"] is False
    assert forbidden["base_branch_head_diff_approved"] is False
    assert any(prefix.startswith("src/environment/") for prefix in FORBIDDEN_PREFIXES)
    assert any(prefix.startswith("src/analysis/state_representation_deadline_queue_feasibility_repair/") for prefix in APPROVED_PREFIXES)


def test_feature_070_prerequisite_report_is_present() -> None:
    status = load_feature_070_status()
    assert status["exists"] is True
    assert status["verified"] is True
    tags = build_prerequisite_tags(True, True, True)
    assert any(tag["name"] == "feature_070_report_valid" for tag in tags)

