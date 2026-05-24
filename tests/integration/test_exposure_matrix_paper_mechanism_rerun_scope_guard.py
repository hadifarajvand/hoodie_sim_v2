from __future__ import annotations

import unittest
from pathlib import Path
from subprocess import run


class ExposureMatrixPaperMechanismRerunScopeGuardTests(unittest.TestCase):
    def test_hard_prerequisite_main_matches_feature_052_commit(self) -> None:
        main_commit = run(["git", "rev-parse", "main"], check=True, capture_output=True, text=True).stdout.strip()
        feature_052_commit = run(["git", "rev-parse", "052-selected-action-outcome-evidence-rerun-complete^{}"], check=True, capture_output=True, text=True).stdout.strip()
        self.assertEqual(main_commit, feature_052_commit)

    def test_committed_artifact_inputs_are_not_rewritten_in_branch_diff(self) -> None:
        diff = run(["git", "diff", "--name-only", "main...HEAD"], check=True, capture_output=True, text=True).stdout.splitlines()
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
