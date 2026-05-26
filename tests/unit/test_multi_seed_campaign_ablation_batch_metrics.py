from __future__ import annotations

import unittest

from src.analysis.multi_seed_campaign_ablation_batch import build_multi_seed_campaign_ablation_batch_report


class MultiSeedCampaignAblationBatchMetricsTests(unittest.TestCase):
    def test_seed_count_is_bounded_and_aggregation_is_multi_seed(self) -> None:
        payload = build_multi_seed_campaign_ablation_batch_report().to_dict()
        self.assertGreaterEqual(payload["multi_seed_gate_summary"]["seed_count"], 3)
        self.assertTrue(payload["multi_seed_aggregation_summary"]["single_run_limitation_removed"])
        self.assertEqual(payload["multi_seed_aggregation_summary"]["sample_count"], payload["multi_seed_gate_summary"]["seed_count"])

    def test_variant_blockers_are_explicit(self) -> None:
        payload = build_multi_seed_campaign_ablation_batch_report().to_dict()
        variants = payload["ablation_gate_summary"]["variants"]
        blocked = [variant for variant in variants if variant["blocked"]]
        self.assertTrue(blocked)
        for variant in blocked:
            self.assertTrue(variant["blocker_list"])


if __name__ == "__main__":
    unittest.main()
