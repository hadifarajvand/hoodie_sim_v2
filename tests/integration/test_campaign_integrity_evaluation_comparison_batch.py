from __future__ import annotations

import unittest

from src.analysis.campaign_integrity_evaluation_comparison_batch import build_campaign_integrity_evaluation_comparison_batch_report


class CampaignIntegrityEvaluationComparisonBatchIntegrationTests(unittest.TestCase):
    def test_report_passes_with_required_routes(self) -> None:
        payload = build_campaign_integrity_evaluation_comparison_batch_report().to_dict()
        self.assertEqual(payload["final_verdict"], "campaign_integrity_evaluation_comparison_batch_passed")
        self.assertEqual(payload["remaining_blockers"], [])
        self.assertEqual(payload["recommended_next_feature"], "Feature 062 — Multi-Seed Campaign and Ablation Batch")

    def test_comparison_readiness_is_controlled_not_reproduction_claim(self) -> None:
        payload = build_campaign_integrity_evaluation_comparison_batch_report().to_dict()
        self.assertTrue(payload["comparison_report_summary"]["controlled_experiment_data"])
        self.assertFalse(payload["comparison_report_summary"]["paper_reproduction_claim"])
        self.assertFalse(payload["comparison_report_summary"]["superiority_claim"])
        self.assertTrue(payload["comparison_report_summary"]["single_run_limitation"])


if __name__ == "__main__":
    unittest.main()
