from __future__ import annotations

from pathlib import Path
import unittest

from src.analysis.target_update_replay_training_validation import build_target_update_replay_validation_report, run_target_update_replay_validation


class TargetUpdateReplayValidationIntegrationTests(unittest.TestCase):
    def test_report_writes_expected_artifacts(self) -> None:
        report = run_target_update_replay_validation()
        json_path = Path("artifacts/analysis/target-update-replay-training-validation/target-update-replay-validation-report.json")
        md_path = Path("artifacts/analysis/target-update-replay-training-validation/target-update-replay-validation-report.md")
        self.assertTrue(json_path.exists())
        self.assertTrue(md_path.exists())
        payload = build_target_update_replay_validation_report().to_dict()
        self.assertEqual(payload["feature_id"], report.feature_id)
        self.assertEqual(payload["final_verdict"], "target_update_replay_validation_passed")


if __name__ == "__main__":
    unittest.main()
