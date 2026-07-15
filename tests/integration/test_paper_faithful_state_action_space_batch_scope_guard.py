from __future__ import annotations

import unittest
from unittest import mock

from src.analysis.git_base_ref import git_triple_dot_range
from src.analysis.paper_faithful_state_action_space_batch import build_paper_faithful_state_action_space_batch_report
from tests.helpers.git_repo import make_temp_git_repo


class PaperFaithfulStateActionSpaceBatchScopeGuardTests(unittest.TestCase):
    def test_git_status_and_diff_only_show_feature_065_paths(self) -> None:
        repo = make_temp_git_repo()
        self.addCleanup(repo.cleanup)
        repo.commit_file("base.txt", "base\n", "base commit")
        repo.git("checkout", "-b", "feature")
        repo.write("artifacts/analysis/paper-faithful-state-action-space-batch/report.json", "{}\n")
        repo.write("specs/065-paper-faithful-state-action-space-batch/spec.md", "feature\n")
        repo.git("add", "artifacts/analysis/paper-faithful-state-action-space-batch/report.json", "specs/065-paper-faithful-state-action-space-batch/spec.md")
        repo.git("commit", "-m", "feature commit")
        paths = repo.output("status", "--short").splitlines() + repo.output("diff", "--name-only", git_triple_dot_range(repo.root)).splitlines() + repo.output("diff", "--cached", "--name-only").splitlines()
        forbidden_prefixes = (
            ".specify/feature.json",
            "AGENTS.md",
            ".gitignore",
            "src/policies/",
            "artifacts/analysis/final-review-release-gate-batch/",
            "artifacts/analysis/results-export-reproducibility-documentation-batch/",
            "artifacts/analysis/multi-seed-campaign-ablation-batch/",
            "artifacts/analysis/campaign-integrity-evaluation-comparison-batch/",
            "artifacts/analysis/full-paper-default-training-campaign-execution/",
            "requirements",
            "pyproject.toml",
            "poetry.lock",
            "uv.lock",
        )
        approved_prefixes = (
            "artifacts/analysis/paper-faithful-state-action-space-batch/",
            "specs/065-paper-faithful-state-action-space-batch/",
            "src/analysis/paper_faithful_state_action_space_batch/",
            "src/environment/paper_state.py",
            "src/environment/paper_action_space.py",
            "src/environment/paper_load_history.py",
            "src/environment/paper_lstm_forecast.py",
            "tests/unit/test_paper_faithful_state_action_space_batch",
            "tests/unit/test_paper_state_vector.py",
            "tests/unit/test_paper_action_space.py",
            "tests/unit/test_paper_load_history.py",
            "tests/integration/test_paper_faithful_state_action_space_batch",
        )
        for path in paths:
            for forbidden in forbidden_prefixes:
                self.assertFalse(path.startswith(forbidden), msg=f"forbidden path present: {path}")
            if path:
                self.assertTrue(any(path.startswith(prefix) for prefix in approved_prefixes), msg=f"unexpected path: {path}")

    def test_report_blocks_forbidden_dirty_paths(self) -> None:
        import src.analysis.paper_faithful_state_action_space_batch.runner as runner

        with mock.patch.object(runner, "_status_paths", return_value=["src/policies/example.py"]):
            with mock.patch.object(runner, "_staged_paths", return_value=[]):
                with mock.patch.object(runner, "_diff_paths", return_value=[]):
                    payload = build_paper_faithful_state_action_space_batch_report().to_dict()
        self.assertFalse(payload["safety_summary"]["no_policy_drift"])


if __name__ == "__main__":
    unittest.main()
