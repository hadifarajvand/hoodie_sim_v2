from __future__ import annotations

import unittest
from pathlib import Path

from src.analysis.git_base_ref import git_triple_dot_range
from tests.helpers.git_repo import make_temp_git_repo


class ExposureMatrixPaperMechanismRerunScopeGuardTests(unittest.TestCase):
    def test_hard_prerequisite_main_matches_feature_052_commit(self) -> None:
        repo = make_temp_git_repo()
        self.addCleanup(repo.cleanup)
        repo.commit_file("base.txt", "base\n", "base commit")
        main_commit = repo.output("rev-parse", "main")
        feature_052_commit = repo.output("rev-parse", "HEAD")
        self.assertEqual(main_commit, feature_052_commit)

    def test_committed_artifact_inputs_are_not_rewritten_in_branch_diff(self) -> None:
        repo = make_temp_git_repo()
        self.addCleanup(repo.cleanup)
        repo.commit_file("base.txt", "base\n", "base commit")
        repo.git("checkout", "-b", "feature")
        repo.write("specs/052-selected-action-outcome-evidence-rerun/spec.md", "feature\n")
        repo.git("add", "specs/052-selected-action-outcome-evidence-rerun/spec.md")
        repo.git("commit", "-m", "feature commit")
        diff = repo.output("diff", "--name-only", git_triple_dot_range(repo.root)).splitlines()
        forbidden_prefixes = (
            "artifacts/analysis/legality-evidence-expansion/",
            "artifacts/analysis/exposure-matrix-paper-mechanism-alignment/",
            "artifacts/analysis/selected-action-family-per-action-outcome-evidence/",
            "artifacts/analysis/passive-selected-action-trace-repair/",
            "artifacts/analysis/selected-action-outcome-evidence-rerun/",
        )
        for path in diff:
            self.assertFalse(path.startswith(forbidden_prefixes), path)

    def test_required_committed_inputs_exist(self) -> None:
        for path in (
            "artifacts/analysis/legality-evidence-expansion/legality-evidence-report.json",
            "artifacts/analysis/exposure-matrix-paper-mechanism-alignment/exposure-matrix-paper-mechanism-report.json",
            "artifacts/analysis/selected-action-family-per-action-outcome-evidence/selected-action-family-outcome-evidence-report.json",
            "artifacts/analysis/passive-selected-action-trace-repair/passive-selected-action-trace-repair-report.json",
            "artifacts/analysis/selected-action-outcome-evidence-rerun/selected-action-outcome-evidence-rerun-report.json",
        ):
            self.assertTrue(Path(path).exists(), path)


if __name__ == "__main__":
    unittest.main()
