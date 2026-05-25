from __future__ import annotations

import subprocess
import unittest
from unittest import mock

from src.analysis.full_paper_default_training_campaign_gate import build_full_paper_default_training_campaign_gate_report


class FullPaperDefaultTrainingCampaignGateScopeGuardTests(unittest.TestCase):
    def test_git_status_and_diff_only_show_feature_059_paths(self) -> None:
        status_output = subprocess.run(["git", "status", "--short"], check=True, capture_output=True, text=True).stdout.splitlines()
        diff_output = subprocess.run(["git", "diff", "--name-only", "main...HEAD"], check=True, capture_output=True, text=True).stdout.splitlines()
        cached_output = subprocess.run(["git", "diff", "--cached", "--name-only"], check=True, capture_output=True, text=True).stdout.splitlines()

        paths = [line[3:].strip() for line in status_output] + [line.strip() for line in diff_output + cached_output]
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
        self.assertEqual(cached_output, [])

    def test_report_blocks_forbidden_dirty_paths(self) -> None:
        import src.analysis.full_paper_default_training_campaign_gate.runner as runner

        with mock.patch.object(runner, "_status_paths", return_value=["src/policies/example.py"]):
            with mock.patch.object(runner, "_staged_paths", return_value=[]):
                with mock.patch.object(runner, "_diff_names", return_value=[]):
                    payload = build_full_paper_default_training_campaign_gate_report().to_dict()
        self.assertEqual(payload["final_verdict"], "behavior_drift_detected")
        self.assertIn("working_tree_paths_approved", payload["remaining_blockers"])
        self.assertFalse(payload["safety_summary"]["no_policy_drift"])


if __name__ == "__main__":
    unittest.main()
