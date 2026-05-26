from __future__ import annotations

import unittest

from src.analysis.multi_seed_campaign_ablation_batch import build_multi_seed_campaign_ablation_batch_report


class MultiSeedCampaignAblationBatchBehaviorEquivalenceTests(unittest.TestCase):
    def test_seed_and_variant_schemas_match(self) -> None:
        payload = build_multi_seed_campaign_ablation_batch_report().to_dict()
        seed_schemas = [result["metric_schema"] for result in payload["multi_seed_campaign_summary"]["seed_level_results"]]
        self.assertTrue(all(schema == seed_schemas[0] for schema in seed_schemas))
        self.assertEqual(len({variant["variant_id"] for variant in payload["ablation_gate_summary"]["variants"]}), len(payload["ablation_gate_summary"]["variants"]))

    def test_no_reproduction_or_superiority_claims(self) -> None:
        payload = build_multi_seed_campaign_ablation_batch_report().to_dict()
        self.assertTrue(payload["safety_summary"]["no_paper_reproduction_claim"])
        self.assertTrue(payload["safety_summary"]["no_unsupported_superiority_claim"])


if __name__ == "__main__":
    unittest.main()
