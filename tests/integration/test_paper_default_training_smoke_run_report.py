from __future__ import annotations

from pathlib import Path
import json
import unittest

from src.analysis.paper_default_training_smoke_run import build_paper_default_training_smoke_report, generate_paper_default_training_smoke_artifacts


class PaperDefaultTrainingSmokeRunReportIntegrationTests(unittest.TestCase):
    def test_report_payload_round_trip(self) -> None:
        report, json_path, md_path = generate_paper_default_training_smoke_artifacts()
        self.assertTrue(json_path.exists())
        self.assertTrue(md_path.exists())
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["feature_id"], report.feature_id)
        self.assertEqual(payload["final_verdict"], "paper_default_training_smoke_passed")
        self.assertEqual(payload["recommended_next_feature"], "Feature 056 — Target Update and Replay Training Validation")

    def test_markdown_report_mentions_the_smoke_scope(self) -> None:
        generate_paper_default_training_smoke_artifacts()
        md_path = Path("artifacts/analysis/paper-default-training-smoke-run/paper-default-training-smoke-run-report.md")
        markdown = md_path.read_text(encoding="utf-8")
        self.assertIn("Paper-Default Training Smoke Run Report", markdown)
        self.assertIn("## Replay Summary", markdown)
        self.assertIn("## Checkpoint Summary", markdown)


if __name__ == "__main__":
    unittest.main()
