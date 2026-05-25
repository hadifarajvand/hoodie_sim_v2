from __future__ import annotations

import json
from pathlib import Path
import unittest

from src.analysis.full_paper_default_training_campaign_gate import generate_full_paper_default_training_campaign_gate_artifacts


class FullPaperDefaultTrainingCampaignGateReportIntegrationTests(unittest.TestCase):
    def test_report_artifacts_are_generated(self) -> None:
        report, json_path, md_path = generate_full_paper_default_training_campaign_gate_artifacts()
        self.assertTrue(json_path.exists())
        self.assertTrue(md_path.exists())
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["feature_id"], report.feature_id)
        self.assertEqual(payload["final_verdict"], "full_paper_default_training_campaign_gate_ready")
        self.assertEqual(payload["remaining_blockers"], [])

    def test_markdown_report_mentions_required_sections(self) -> None:
        generate_full_paper_default_training_campaign_gate_artifacts()
        markdown = Path("artifacts/analysis/full-paper-default-training-campaign-gate/full-paper-default-training-campaign-gate-report.md").read_text(encoding="utf-8")
        self.assertIn("Full Paper-Default Training Campaign Gate Report", markdown)
        self.assertIn("## Campaign Scope Summary", markdown)
        self.assertIn("## Resource Control Summary", markdown)
        self.assertIn("## Checkpoint Contract Summary", markdown)

    def test_report_does_not_claim_reproduction_performance_or_baseline_superiority(self) -> None:
        payload = generate_full_paper_default_training_campaign_gate_artifacts()[0].to_dict()
        self.assertTrue(payload["safety_summary"]["no_paper_reproduction_claim"])
        self.assertTrue(payload["safety_summary"]["no_performance_claim"])
        self.assertTrue(payload["safety_summary"]["no_baseline_superiority_claim"])
        self.assertFalse(payload["campaign_scope_summary"]["full_campaign_executed_this_feature"])


if __name__ == "__main__":
    unittest.main()
