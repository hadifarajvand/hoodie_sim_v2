from __future__ import annotations

import unittest

from src.analysis.bind_full_campaign_real_torch_trainer import build_bind_full_campaign_real_torch_trainer_report
from src.analysis.bind_full_campaign_real_torch_trainer.config import FEATURE_ID, REQUIRED_TOP_LEVEL_FIELDS
from src.analysis.bind_full_campaign_real_torch_trainer.model import BindFullCampaignRealTorchTrainerReport


class BindFullCampaignRealTorchTrainerSchemaTests(unittest.TestCase):
    def test_report_has_required_fields_and_pass_verdict(self) -> None:
        payload = build_bind_full_campaign_real_torch_trainer_report().to_dict()
        for key in REQUIRED_TOP_LEVEL_FIELDS:
            self.assertIn(key, payload)
        self.assertEqual(payload["feature_id"], FEATURE_ID)
        self.assertEqual(payload["final_verdict"], "real_torch_trainer_binding_repair_passed")
        self.assertEqual(payload["remaining_blockers"], [])

    def test_pass_with_blockers_is_rejected(self) -> None:
        payload = build_bind_full_campaign_real_torch_trainer_report().to_dict()
        payload["remaining_blockers"] = ["feature_060_real_trainer_binding_not_verified"]
        with self.assertRaises(ValueError):
            BindFullCampaignRealTorchTrainerReport(**payload)


if __name__ == "__main__":
    unittest.main()
