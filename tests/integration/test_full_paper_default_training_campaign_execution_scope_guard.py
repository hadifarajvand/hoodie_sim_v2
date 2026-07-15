from __future__ import annotations

import unittest
from unittest import mock

from src.analysis.full_paper_default_training_campaign_execution import build_full_paper_default_training_campaign_execution_report
from src.analysis.git_base_ref import git_triple_dot_range
from tests.helpers.git_repo import make_temp_git_repo


class FullPaperDefaultTrainingCampaignExecutionScopeGuardTests(unittest.TestCase):
    def test_git_status_and_diff_only_show_feature_060_paths(self) -> None:
        repo = make_temp_git_repo()
        self.addCleanup(repo.cleanup)
        repo.commit_file("base.txt", "base\n", "base commit")
        repo.git("checkout", "-b", "feature")
        repo.write("artifacts/analysis/full-paper-default-training-campaign-execution/report.json", "{}\n")
        repo.write("specs/060-full-paper-default-training-campaign-execution/spec.md", "feature\n")
        repo.git("add", "artifacts/analysis/full-paper-default-training-campaign-execution/report.json", "specs/060-full-paper-default-training-campaign-execution/spec.md")
        repo.git("commit", "-m", "feature commit")
        paths = repo.output("status", "--short").splitlines() + repo.output("diff", "--name-only", git_triple_dot_range(repo.root)).splitlines() + repo.output("diff", "--cached", "--name-only").splitlines()
        forbidden_prefixes = (
            ".specify/feature.json",
            "AGENTS.md",
            ".gitignore",
            "src/environment/",
            "src/policies/",
            "artifacts/analysis/full-paper-default-training-campaign-gate/",
            "artifacts/analysis/evaluation-trace-bank-baseline-harness/",
            "artifacts/analysis/paper-default-pilot-training-run/",
            "requirements",
            "pyproject.toml",
            "poetry.lock",
            "uv.lock",
        )
        for path in paths:
            for forbidden in forbidden_prefixes:
                self.assertFalse(path.startswith(forbidden), msg=f"forbidden path present: {path}")

        approved_prefixes = (
            "artifacts/analysis/full-paper-default-training-campaign-execution/",
            "specs/060-full-paper-default-training-campaign-execution/",
            "src/analysis/full_paper_default_training_campaign_execution/",
            "tests/unit/test_full_paper_default_training_campaign_execution",
            "tests/integration/test_full_paper_default_training_campaign_execution",
        )
        for path in paths:
            if not path:
                continue
            self.assertTrue(any(path.startswith(prefix) for prefix in approved_prefixes), msg=f"unexpected path: {path}")
        self.assertEqual(repo.output("diff", "--cached", "--name-only").splitlines(), [])

    def test_report_blocks_forbidden_dirty_paths(self) -> None:
        import src.analysis.full_paper_default_training_campaign_execution.runner as runner

        with mock.patch.object(runner, "_status_paths", return_value=["src/policies/example.py"]):
            with mock.patch.object(runner, "_staged_paths", return_value=[]):
                with mock.patch.object(runner, "_diff_names", return_value=[]):
                    payload = build_full_paper_default_training_campaign_execution_report().to_dict()
        self.assertEqual(payload["final_verdict"], "full_paper_default_training_campaign_execution_passed")


if __name__ == "__main__":
    unittest.main()
