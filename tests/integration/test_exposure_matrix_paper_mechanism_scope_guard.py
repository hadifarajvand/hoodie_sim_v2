from __future__ import annotations

import json
import unittest
from pathlib import Path

from src.analysis.git_base_ref import git_triple_dot_range
from tests.helpers.git_repo import make_temp_git_repo


class ExposureMatrixPaperMechanismScopeGuardTests(unittest.TestCase):
    def test_spec_pointer_points_to_feature_049_and_is_local_only(self) -> None:
        repo = make_temp_git_repo()
        self.addCleanup(repo.cleanup)
        repo.commit_file("base.txt", "base\n", "base commit")
        repo.git("checkout", "-b", "feature")
        repo.write(".specify/feature.json", json.dumps({"feature_directory": "specs/049-exposure-matrix-paper-mechanism-alignment"}) + "\n")
        repo.write("artifacts/analysis/exposure-matrix-paper-mechanism-alignment/report.json", "{}\n")
        repo.write("specs/049-exposure-matrix-paper-mechanism-alignment/spec.md", "feature\n")
        repo.git("add", "artifacts/analysis/exposure-matrix-paper-mechanism-alignment/report.json", "specs/049-exposure-matrix-paper-mechanism-alignment/spec.md")
        repo.git("commit", "-m", "feature commit")
        pointer = json.loads((repo.root / ".specify/feature.json").read_text(encoding="utf-8"))
        self.assertEqual(pointer["feature_directory"], "specs/049-exposure-matrix-paper-mechanism-alignment")
        self.assertEqual(repo.output("diff", "--cached", "--name-only").strip(), "")
        self.assertNotIn(".specify/feature.json", repo.output("diff", "--name-only", git_triple_dot_range(repo.root)).splitlines())

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
