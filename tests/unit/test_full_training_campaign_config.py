from __future__ import annotations

import unittest

from src.analysis.full_training_reproduction_campaign import CampaignConfig, PilotBudget, TargetUpdateContract


class FullTrainingCampaignConfigUnitTests(unittest.TestCase):
    def test_target_update_unit_requires_explicit_approval(self) -> None:
        with self.assertRaises(ValueError):
            TargetUpdateContract(target_update_unit="episode")

    def test_target_update_unit_records_optimizer_step_as_user_approved_assumption(self) -> None:
        contract = TargetUpdateContract()
        self.assertEqual(contract.update_frequency, 2000)
        self.assertEqual(contract.target_update_unit, "optimizer_step")
        self.assertEqual(contract.approval_status, "user_approved_campaign_assumption")
        self.assertEqual(contract.paper_evidence_status, "ambiguous_not_explicitly_defined")
        self.assertTrue(contract.should_sync(2000))
        self.assertFalse(contract.should_sync(1999))

    def test_campaign_config_preserves_staged_budgets_and_manual_approval_contract(self) -> None:
        config = CampaignConfig()
        self.assertEqual(config.feature_id, "041-full-training-reproduction-campaign")
        self.assertEqual(config.state_dim, 3)
        self.assertEqual(config.action_count, 3)
        self.assertEqual(config.lookback_w, 10)
        self.assertEqual(config.q_network_hidden_layers, [1024, 1024, 1024])
        self.assertEqual(config.lstm_num_layers, 1)
        self.assertEqual(config.lstm_hidden_size, 20)
        self.assertEqual(config.model_initialization_seed, 19)
        self.assertEqual(config.pilot_budget, PilotBudget())
        self.assertEqual(config.full_campaign_budget, 5000)
        self.assertFalse(config.full_campaign_enabled)
        self.assertTrue(config.readiness_manual_approval_required)
        self.assertEqual(config.readiness_manual_approval_status, "not_approved")
        self.assertEqual(config.readiness_manual_approval_reference, "")
        self.assertEqual(config.target_update_contract.target_update_unit, "optimizer_step")

    def test_campaign_config_rejects_sloppy_n_l_coupling(self) -> None:
        with self.assertRaises(ValueError):
            CampaignConfig(q_network_hidden_layers=[20])
        with self.assertRaises(ValueError):
            CampaignConfig(q_network_hidden_layers=20)  # type: ignore[arg-type]

    def test_campaign_config_rejects_approved_readiness_without_reference(self) -> None:
        with self.assertRaises(ValueError):
            CampaignConfig(readiness_manual_approval_status="approved")

    def test_campaign_config_allows_approved_readiness_with_reference(self) -> None:
        config = CampaignConfig(
            readiness_manual_approval_status="approved",
            readiness_manual_approval_reference="user-approval-041",
        )
        self.assertEqual(config.readiness_manual_approval_status, "approved")
        self.assertEqual(config.readiness_manual_approval_reference, "user-approval-041")


if __name__ == "__main__":
    unittest.main()
