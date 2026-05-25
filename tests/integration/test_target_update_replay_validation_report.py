from __future__ import annotations

from pathlib import Path
import json
import unittest

from src.analysis.target_update_replay_training_validation import build_target_update_replay_validation_report, generate_target_update_replay_validation_artifacts


class TargetUpdateReplayValidationReportIntegrationTests(unittest.TestCase):
    def test_report_payload_round_trip(self) -> None:
        report, json_path, md_path = generate_target_update_replay_validation_artifacts()
        self.assertTrue(json_path.exists())
        self.assertTrue(md_path.exists())
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["feature_id"], report.feature_id)
        self.assertEqual(payload["final_verdict"], "target_update_replay_validation_passed")
        self.assertEqual(payload["recommended_next_feature"], "Feature 057 — Paper-Default Pilot Training Run")

    def test_markdown_report_mentions_the_validation_scope(self) -> None:
        generate_target_update_replay_validation_artifacts()
        md_path = Path("artifacts/analysis/target-update-replay-training-validation/target-update-replay-validation-report.md")
        markdown = md_path.read_text(encoding="utf-8")
        self.assertIn("Target Update and Replay Training Validation Report", markdown)
        self.assertIn("## Replay Summary", markdown)
        self.assertIn("## Target Update Summary", markdown)


if __name__ == "__main__":
    unittest.main()
