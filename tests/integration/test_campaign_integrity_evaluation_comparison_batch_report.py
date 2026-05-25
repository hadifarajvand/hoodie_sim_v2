from __future__ import annotations

import json
from pathlib import Path
import unittest

from src.analysis.campaign_integrity_evaluation_comparison_batch import generate_campaign_integrity_evaluation_comparison_batch_artifacts
from src.analysis.campaign_integrity_evaluation_comparison_batch.config import REPORT_JSON, REPORT_MD


class CampaignIntegrityEvaluationComparisonBatchReportIntegrationTests(unittest.TestCase):
    def test_report_artifacts_are_generated(self) -> None:
        report, json_path, md_path = generate_campaign_integrity_evaluation_comparison_batch_artifacts()
        self.assertEqual(json_path, REPORT_JSON)
        self.assertEqual(md_path, REPORT_MD)
        self.assertTrue(json_path.exists())
        self.assertTrue(md_path.exists())
        self.assertEqual(json.loads(json_path.read_text(encoding="utf-8")), report.to_dict())

    def test_markdown_report_mentions_required_sections(self) -> None:
        generate_campaign_integrity_evaluation_comparison_batch_artifacts()
        markdown = Path(REPORT_MD).read_text(encoding="utf-8")
        self.assertIn("Campaign Integrity Evaluation Comparison Batch Report", markdown)
        self.assertIn("## Campaign Integrity Summary", markdown)
        self.assertIn("## Comparison Readiness Summary", markdown)
        self.assertIn("## Comparison Report Summary", markdown)


if __name__ == "__main__":
    unittest.main()
