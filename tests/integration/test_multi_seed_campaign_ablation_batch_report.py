from __future__ import annotations

import unittest

from src.analysis.multi_seed_campaign_ablation_batch import generate_multi_seed_campaign_ablation_batch_artifacts
from src.analysis.multi_seed_campaign_ablation_batch.config import REPORT_MD, REPORT_JSON


class MultiSeedCampaignAblationBatchReportTests(unittest.TestCase):
    def test_markdown_and_json_reports_are_generated(self) -> None:
        generate_multi_seed_campaign_ablation_batch_artifacts()
        self.assertTrue(REPORT_JSON.exists())
        self.assertTrue(REPORT_MD.exists())
        text = REPORT_MD.read_text(encoding="utf-8")
        self.assertIn("multi_seed_campaign_ablation_batch_passed", text)


if __name__ == "__main__":
    unittest.main()
