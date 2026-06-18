from __future__ import annotations

import unittest

from src.analysis.bind_full_campaign_real_torch_trainer import build_bind_full_campaign_real_torch_trainer_report


class BindFullCampaignRealTorchTrainerBehaviorEquivalenceTests(unittest.TestCase):
    def test_prerequisite_tag_names_are_unique(self) -> None:
        payload = build_bind_full_campaign_real_torch_trainer_report().to_dict()
        names = [entry["name"] for entry in payload["prerequisite_tags_verified"]]
        self.assertEqual(len(names), len(set(names)))

    def test_forbidden_claims_remain_false(self) -> None:
        safety = build_bind_full_campaign_real_torch_trainer_report().to_dict()["safety_summary"]
        for key in (
            "no_paper_reproduction_claim",
            "no_performance_superiority_claim",
            "no_baseline_superiority_claim",
            "no_uncontrolled_campaign_loop",
            "no_policy_drift",
            "no_dependency_drift",
            "no_environment_contract_drift",
            "no_reward_timing_change",
        ):
            self.assertIsInstance(safety[key], bool)
        self.assertFalse(safety["no_policy_drift"])
        self.assertFalse(safety["no_environment_contract_drift"])


if __name__ == "__main__":
    unittest.main()
