from __future__ import annotations

import json
import unittest
from pathlib import Path
from subprocess import run


class ExposureMatrixPaperMechanismScopeGuardTests(unittest.TestCase):
    def test_spec_pointer_points_to_feature_049_and_is_local_only(self) -> None:
        pointer = json.loads(Path(".specify/feature.json").read_text(encoding="utf-8"))
        self.assertEqual(pointer["feature_directory"], "specs/049-exposure-matrix-paper-mechanism-alignment")
        self.assertEqual(run(["git", "diff", "--cached", "--name-only"], check=True, capture_output=True, text=True).stdout.strip(), "")
        self.assertNotIn(".specify/feature.json", run(["git", "diff", "--name-only", "main...HEAD"], check=True, capture_output=True, text=True).stdout.splitlines())

    def test_committed_artifact_prerequisites_are_present(self) -> None:
        for path in (
            "artifacts/analysis/task-completion-lifecycle-formula-audit/completion-lifecycle-audit-report.json",
            "artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/lifecycle-trace-instrumentation-report.json",
            "artifacts/analysis/completion-root-cause-diagnosis/completion-root-cause-report.json",
            "artifacts/analysis/load-admission-action-exposure-review/load-admission-action-exposure-report.json",
            "artifacts/analysis/exposure-matrix-review/exposure-matrix-report.json",
            "artifacts/analysis/legality-evidence-expansion/legality-evidence-report.json",
        ):
            self.assertTrue(Path(path).exists(), path)


if __name__ == "__main__":
    unittest.main()
