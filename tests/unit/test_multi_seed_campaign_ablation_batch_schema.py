from __future__ import annotations

import unittest

from src.analysis.multi_seed_campaign_ablation_batch import build_multi_seed_campaign_ablation_batch_report
from src.analysis.multi_seed_campaign_ablation_batch.config import FEATURE_ID, REQUIRED_TOP_LEVEL_FIELDS
from src.analysis.multi_seed_campaign_ablation_batch.model import MultiSeedCampaignAblationBatchReport


class MultiSeedCampaignAblationBatchSchemaTests(unittest.TestCase):
    def test_report_has_required_fields_and_pass_or_blocked_verdict(self) -> None:
        payload = build_multi_seed_campaign_ablation_batch_report().to_dict()
        for key in REQUIRED_TOP_LEVEL_FIELDS:
            self.assertIn(key, payload)
        self.assertEqual(payload["feature_id"], FEATURE_ID)

    def test_pass_with_blockers_is_rejected(self) -> None:
        payload = build_multi_seed_campaign_ablation_batch_report().to_dict()
        payload["remaining_blockers"] = ["feature_061_prerequisite_blocked"]
        payload["final_verdict"] = "multi_seed_campaign_ablation_batch_passed"
        with self.assertRaises(ValueError):
            MultiSeedCampaignAblationBatchReport(**payload)


if __name__ == "__main__":
    unittest.main()
