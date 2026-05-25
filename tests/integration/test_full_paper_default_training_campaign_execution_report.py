from __future__ import annotations

import json
from pathlib import Path
import unittest

from src.analysis.full_paper_default_training_campaign_execution import generate_full_paper_default_training_campaign_execution_artifacts


class FullPaperDefaultTrainingCampaignExecutionReportIntegrationTests(unittest.TestCase):
    def test_report_artifacts_are_generated(self) -> None:
        report, json_path, md_path = generate_full_paper_default_training_campaign_execution_artifacts()
        self.assertTrue(json_path.exists())
        self.assertTrue(md_path.exists())
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["feature_id"], report.feature_id)
        self.assertEqual(payload["final_verdict"], "full_paper_default_training_campaign_execution_passed")
        self.assertEqual(payload["remaining_blockers"], [])

    def test_markdown_report_mentions_required_sections(self) -> None:
        generate_full_paper_default_training_campaign_execution_artifacts()
        markdown = Path("artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.md").read_text(encoding="utf-8")
        self.assertIn("Full Paper-Default Training Campaign Execution Report", markdown)
        self.assertIn("## Campaign Execution Summary", markdown)
        self.assertIn("## Training Metrics Summary", markdown)
        self.assertIn("## Artifact Manifest Summary", markdown)

    def test_report_does_not_claim_reproduction_or_superiority(self) -> None:
        payload = generate_full_paper_default_training_campaign_execution_artifacts()[0].to_dict()
        self.assertTrue(payload["safety_summary"]["no_paper_reproduction_claim"])
        self.assertTrue(payload["safety_summary"]["no_performance_superiority_claim"])
        self.assertTrue(payload["safety_summary"]["no_baseline_superiority_claim"])
        self.assertTrue(payload["safety_summary"]["no_uncontrolled_campaign_loop"])


if __name__ == "__main__":
    unittest.main()
