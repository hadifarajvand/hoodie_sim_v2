from __future__ import annotations

from src.analysis.final_review_release_gate_batch.runner import _path_classification, _status_paths


def test_scope_guard_recognizes_allowed_and_forbidden_paths() -> None:
    allowed = [
        "src/analysis/final_review_release_gate_batch/runner.py",
        "tests/unit/test_final_review_release_gate_batch_schema.py",
    ]
    forbidden = [
        "src/environment/runtime_model.py",
        "src/policies/something.py",
        "requirements.txt",
    ]

    assert _path_classification(allowed)["approved"] is True
    assert _path_classification(forbidden)["approved"] is False


def test_current_worktree_changes_stay_inside_the_feature_scope() -> None:
    paths = _status_paths()
    assert paths
    assert all(
        path.startswith("specs/064-final-review-release-gate-batch/")
        or path.startswith("src/analysis/final_review_release_gate_batch/")
        or path.startswith("tests/unit/test_final_review_release_gate_batch")
        or path.startswith("tests/integration/test_final_review_release_gate_batch")
        or path.startswith("docs/architecture/euls_phase23_final_review_release_gate_batch.md")
        or path.startswith("artifacts/analysis/final-review-release-gate-batch/")
        for path in paths
    )
