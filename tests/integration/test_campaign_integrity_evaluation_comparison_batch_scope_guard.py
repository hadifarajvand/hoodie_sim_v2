from __future__ import annotations

import subprocess
import unittest
from unittest import mock

from src.analysis.campaign_integrity_evaluation_comparison_batch import build_campaign_integrity_evaluation_comparison_batch_report


class CampaignIntegrityEvaluationComparisonBatchScopeGuardTests(unittest.TestCase):
    def test_git_status_and_diff_only_show_feature_061_paths(self) -> None:
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
            "artifacts/analysis/full-paper-default-training-campaign-execution/",
            "artifacts/analysis/bind-full-campaign-real-torch-trainer/",
            "artifacts/analysis/evaluation-trace-bank-baseline-harness/",
            "requirements",
            "pyproject.toml",
            "poetry.lock",
            "uv.lock",
        )
        approved_prefixes = (
            "artifacts/analysis/campaign-integrity-evaluation-comparison-batch/",
            "specs/061-campaign-integrity-evaluation-comparison-batch/",
            "src/analysis/campaign_integrity_evaluation_comparison_batch/",
            "tests/unit/test_campaign_integrity_evaluation_comparison_batch",
            "tests/integration/test_campaign_integrity_evaluation_comparison_batch",
        )
        for path in paths:
            for forbidden in forbidden_prefixes:
                self.assertFalse(path.startswith(forbidden), msg=f"forbidden path present: {path}")
            if path:
                self.assertTrue(any(path.startswith(prefix) for prefix in approved_prefixes), msg=f"unexpected path: {path}")

    def test_report_blocks_forbidden_dirty_paths(self) -> None:
        import src.analysis.campaign_integrity_evaluation_comparison_batch.runner as runner

        with mock.patch.object(runner, "_status_paths", return_value=["src/policies/example.py"]):
            with mock.patch.object(runner, "_staged_paths", return_value=[]):
                with mock.patch.object(runner, "_diff_paths", return_value=[]):
                    payload = build_campaign_integrity_evaluation_comparison_batch_report().to_dict()
        self.assertEqual(payload["final_verdict"], "behavior_drift_detected")
        self.assertIn("behavior_drift_detected", payload["remaining_blockers"])
        self.assertFalse(payload["safety_summary"]["no_policy_drift"])


if __name__ == "__main__":
    unittest.main()
