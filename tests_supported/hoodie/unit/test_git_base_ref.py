from __future__ import annotations

from pathlib import Path

import pytest

from src.analysis.git_base_ref import (
    GitBaseRefResolutionError,
    committed_changed_files,
    comparison_range,
    is_worktree_dirty,
    repository_head,
    resolve_base_ref,
)
from tests.helpers.git_repo import make_temp_git_repo


def test_resolve_base_ref_prefers_explicit_base_over_fallbacks() -> None:
    repo = make_temp_git_repo()
    try:
        repo.commit_file("tracked.txt", "base\n", "base")
        repo.git("branch", "feature")
        repo.git("checkout", "feature")
        repo.commit_file("tracked.txt", "feature\n", "feature")

        assert resolve_base_ref(repo.root, explicit_base="main") == "main"
        assert comparison_range(repo.root, explicit_base="main") == "main...HEAD"
        assert committed_changed_files(repo.root, "main") == ["tracked.txt"]
        assert repository_head(repo.root)
        assert not is_worktree_dirty(repo.root)
    finally:
        repo.cleanup()


def test_resolve_base_ref_raises_when_no_base_exists() -> None:
    repo = make_temp_git_repo()
    try:
        repo.commit_file("tracked.txt", "base\n", "base")
        repo.git("branch", "feature")
        repo.git("checkout", "feature")
        repo.write("tracked.txt", "dirty\n")

        with pytest.raises(GitBaseRefResolutionError):
            resolve_base_ref(repo.root, explicit_base="missing-base")
    finally:
        repo.cleanup()
