from __future__ import annotations

import subprocess
import unittest
from unittest import mock

from src.analysis.paper_faithful_state_action_space_batch import build_paper_faithful_state_action_space_batch_report


class PaperFaithfulStateActionSpaceBatchScopeGuardTests(unittest.TestCase):
    def test_git_status_and_diff_only_show_feature_065_paths(self) -> None:
        status_output = subprocess.run(["git", "status", "--short"], check=True, capture_output=True, text=True).stdout.splitlines()
        diff_output = subprocess.run(["git", "diff", "--name-only", "main...HEAD"], check=True, capture_output=True, text=True).stdout.splitlines()
        cached_output = subprocess.run(["git", "diff", "--cached", "--name-only"], check=True, capture_output=True, text=True).stdout.splitlines()
        paths = [line[3:].strip() for line in status_output] + [line.strip() for line in diff_output + cached_output]
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
            if path and any(path.startswith(prefix) for prefix in approved_prefixes):
                self.assertTrue(any(path.startswith(prefix) for prefix in approved_prefixes), msg=f"unexpected path: {path}")

    def test_report_blocks_forbidden_dirty_paths(self) -> None:
        import src.analysis.paper_faithful_state_action_space_batch.runner as runner

        with mock.patch.object(runner, "_status_paths", return_value=["src/policies/example.py"]):
            with mock.patch.object(runner, "_staged_paths", return_value=[]):
                with mock.patch.object(runner, "_diff_paths", return_value=[]):
                    payload = build_paper_faithful_state_action_space_batch_report().to_dict()
        self.assertEqual(payload["final_verdict"], "behavior_drift_detected")
        self.assertIn("behavior_drift_detected", payload["remaining_blockers"])
        self.assertFalse(payload["safety_summary"]["no_policy_drift"])


if __name__ == "__main__":
    unittest.main()
