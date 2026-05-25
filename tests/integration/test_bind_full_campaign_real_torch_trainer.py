from __future__ import annotations

import json
import unittest

from src.analysis.bind_full_campaign_real_torch_trainer import build_bind_full_campaign_real_torch_trainer_report


class BindFullCampaignRealTorchTrainerIntegrationTests(unittest.TestCase):
    def test_feature_060a_prerequisite_is_verified(self) -> None:
        payload = build_bind_full_campaign_real_torch_trainer_report().to_dict()
        self.assertTrue(payload["feature_060a_audit_verified"])

    def test_regenerated_feature_060_report_supports_claim(self) -> None:
        payload = build_bind_full_campaign_real_torch_trainer_report().to_dict()
        self.assertTrue(payload["feature_060_repair_summary"]["feature_060_claim_supported"])
        feature_060 = json.load(open("artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json"))
        self.assertEqual(feature_060["final_verdict"], "full_paper_default_training_campaign_execution_passed")
        self.assertEqual(feature_060["remaining_blockers"], [])
        self.assertTrue(feature_060["campaign_execution_summary"]["real_trainer_binding"]["real_trainer_instantiated"])


if __name__ == "__main__":
    unittest.main()
