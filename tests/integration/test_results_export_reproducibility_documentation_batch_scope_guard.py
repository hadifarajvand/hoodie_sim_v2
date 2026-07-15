from __future__ import annotations

import unittest
from unittest import mock

from src.analysis.git_base_ref import git_triple_dot_range
from src.analysis.results_export_reproducibility_documentation_batch import build_results_export_reproducibility_documentation_batch_report
from tests.helpers.git_repo import make_temp_git_repo


class ResultsExportReproducibilityDocumentationBatchScopeGuardTests(unittest.TestCase):
    def test_git_status_and_diff_only_show_feature_063_paths(self) -> None:
        repo = make_temp_git_repo()
        self.addCleanup(repo.cleanup)
        repo.commit_file("base.txt", "base\n", "base commit")
        repo.git("checkout", "-b", "feature")
        repo.write("artifacts/analysis/results-export-reproducibility-documentation-batch/report.json", "{}\n")
        repo.write("specs/063-results-export-reproducibility-documentation-batch/spec.md", "feature\n")
        repo.git("add", "artifacts/analysis/results-export-reproducibility-documentation-batch/report.json", "specs/063-results-export-reproducibility-documentation-batch/spec.md")
        repo.git("commit", "-m", "feature commit")
        paths = repo.output("status", "--short").splitlines() + repo.output("diff", "--name-only", git_triple_dot_range(repo.root)).splitlines() + repo.output("diff", "--cached", "--name-only").splitlines()
        forbidden_prefixes = (
            ".specify/feature.json",
            "AGENTS.md",
            ".gitignore",
            "src/environment/",
            "src/policies/",
            "artifacts/analysis/multi-seed-campaign-ablation-batch/",
            "artifacts/analysis/campaign-integrity-evaluation-comparison-batch/",
            "artifacts/analysis/full-paper-default-training-campaign-execution/",
            "requirements",
            "pyproject.toml",
            "poetry.lock",
            "uv.lock",
        )
        approved_prefixes = (
            "artifacts/analysis/results-export-reproducibility-documentation-batch/",
            "specs/063-results-export-reproducibility-documentation-batch/",
            "src/analysis/results_export_reproducibility_documentation_batch/",
            "tests/unit/test_results_export_reproducibility_documentation_batch",
            "tests/integration/test_results_export_reproducibility_documentation_batch",
        )
        for path in paths:
            for forbidden in forbidden_prefixes:
                self.assertFalse(path.startswith(forbidden), msg=f"forbidden path present: {path}")
            if path:
                self.assertTrue(any(path.startswith(prefix) for prefix in approved_prefixes), msg=f"unexpected path: {path}")

    def test_report_blocks_forbidden_dirty_paths(self) -> None:
        import src.analysis.results_export_reproducibility_documentation_batch.runner as runner

        with mock.patch.object(runner, "_status_paths", return_value=["src/policies/example.py"]):
            with mock.patch.object(runner, "_staged_paths", return_value=[]):
                with mock.patch.object(runner, "_diff_paths", return_value=[]):
                    payload = build_results_export_reproducibility_documentation_batch_report().to_dict()
        self.assertFalse(payload["safety_summary"]["no_policy_drift"])


if __name__ == "__main__":
    unittest.main()
