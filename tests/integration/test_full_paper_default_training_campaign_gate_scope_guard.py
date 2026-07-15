from __future__ import annotations

import unittest
from unittest import mock

from src.analysis.full_paper_default_training_campaign_gate import build_full_paper_default_training_campaign_gate_report
from src.analysis.git_base_ref import git_triple_dot_range
from tests.helpers.git_repo import make_temp_git_repo


class FullPaperDefaultTrainingCampaignGateScopeGuardTests(unittest.TestCase):
    def test_git_status_and_diff_only_show_feature_059_paths(self) -> None:
        repo = make_temp_git_repo()
        self.addCleanup(repo.cleanup)
        repo.commit_file("base.txt", "base\n", "base commit")
        repo.git("checkout", "-b", "feature")
        repo.write("artifacts/analysis/full-paper-default-training-campaign-gate/report.json", "{}\n")
        repo.write("specs/059-full-paper-default-training-campaign-gate/spec.md", "feature\n")
        repo.git("add", "artifacts/analysis/full-paper-default-training-campaign-gate/report.json", "specs/059-full-paper-default-training-campaign-gate/spec.md")
        repo.git("commit", "-m", "feature commit")

        paths = repo.output("status", "--short").splitlines() + repo.output("diff", "--name-only", git_triple_dot_range(repo.root)).splitlines() + repo.output("diff", "--cached", "--name-only").splitlines()
        forbidden_prefixes = (
            ".specify/feature.json",
            "AGENTS.md",
            ".gitignore",
            "src/environment/",
            "src/policies/",
            "artifacts/analysis/evaluation-trace-bank-baseline-harness/",
            "artifacts/analysis/paper-default-pilot-training-run/",
            "artifacts/analysis/target-update-replay-training-validation/",
            "artifacts/analysis/paper-default-training-smoke-run/",
            "requirements",
            "pyproject.toml",
            "poetry.lock",
            "uv.lock",
        )
        for path in paths:
            for forbidden in forbidden_prefixes:
                self.assertFalse(path.startswith(forbidden), msg=f"forbidden path present: {path}")

        approved_prefixes = (
            "artifacts/analysis/full-paper-default-training-campaign-gate/",
            "specs/059-full-paper-default-training-campaign-gate/",
            "src/analysis/full_paper_default_training_campaign_gate/",
            "tests/unit/test_full_paper_default_training_campaign_gate",
            "tests/integration/test_full_paper_default_training_campaign_gate",
        )
        for path in paths:
            if not path:
                continue
            self.assertTrue(any(path.startswith(prefix) for prefix in approved_prefixes), msg=f"unexpected path: {path}")
        self.assertEqual(repo.output("diff", "--cached", "--name-only").splitlines(), [])

    def test_report_blocks_forbidden_dirty_paths(self) -> None:
        import src.analysis.full_paper_default_training_campaign_gate.runner as runner

        passing_prerequisites = [
            {"name": "branch", "verified": True},
            {"name": "not_main", "verified": True},
            {"name": "base_contains_feature_058_complete", "verified": True},
            {"name": "base_is_branch_base", "verified": True},
            {"name": "feature_058_report_valid", "verified": True},
            {"name": "feature_057_report_present", "verified": True},
            {"name": "feature_056_report_present", "verified": True},
            {"name": "feature_055_report_present", "verified": True},
            {"name": "working_tree_paths_approved", "verified": False},
            {"name": "staged_paths_approved", "verified": True},
            {"name": "main_head_diff_approved", "verified": True},
            {"name": "agents_stable_not_modified", "verified": True},
            {"name": "pointer_local_only_not_dirty_or_staged", "verified": True},
        ]

        with mock.patch.object(runner, "_status_paths", return_value=["src/policies/example.py"]):
            with mock.patch.object(runner, "_staged_paths", return_value=[]):
                with mock.patch.object(runner, "_diff_names", return_value=[]):
                    with mock.patch.object(runner, "_feature_058_harness_verified", return_value=True):
                        with mock.patch.object(runner, "_build_prerequisite_tags_verified", return_value=passing_prerequisites):
                            payload = build_full_paper_default_training_campaign_gate_report().to_dict()
        self.assertEqual(payload["final_verdict"], "behavior_drift_detected")
        self.assertIn("working_tree_paths_approved", payload["remaining_blockers"])
        self.assertFalse(payload["safety_summary"]["no_policy_drift"])


if __name__ == "__main__":
    unittest.main()
