from __future__ import annotations

import unittest

from src.analysis.full_training_reproduction_campaign import CampaignConfig


class PaperDefaultCampaignConfigUnitTests(unittest.TestCase):
    def test_paper_default_has_correct_state_dim(self) -> None:
        config = CampaignConfig.paper_default()
        self.assertEqual(config.state_dim, 74)

    def test_paper_default_has_correct_action_count(self) -> None:
        config = CampaignConfig.paper_default()
        self.assertEqual(config.action_count, 22)

    def test_paper_default_has_correct_lookback_w(self) -> None:
        config = CampaignConfig.paper_default()
        self.assertEqual(config.lookback_w, 10)

    def test_paper_default_has_correct_network_layers(self) -> None:
        config = CampaignConfig.paper_default()
        self.assertEqual(config.q_network_hidden_layers, [1024, 1024, 1024])

    def test_paper_default_has_correct_lstm_config(self) -> None:
        config = CampaignConfig.paper_default()
        self.assertEqual(config.lstm_num_layers, 1)
        self.assertEqual(config.lstm_hidden_size, 20)

    def test_paper_default_has_correct_model_initialization_seed(self) -> None:
        config = CampaignConfig.paper_default()
        self.assertEqual(config.model_initialization_seed, 19)

    def test_paper_default_has_correct_learning_rate(self) -> None:
        config = CampaignConfig.paper_default()
        self.assertEqual(config.learning_rate, 7e-7)

    def test_paper_default_has_correct_gamma(self) -> None:
        config = CampaignConfig.paper_default()
        self.assertEqual(config.gamma, 0.99)

    def test_paper_default_has_correct_batch_size(self) -> None:
        config = CampaignConfig.paper_default()
        self.assertEqual(config.batch_size, 64)

    def test_paper_default_has_correct_replay_memory_capacity(self) -> None:
        config = CampaignConfig.paper_default()
        self.assertEqual(config.replay_memory_capacity, 10_000)

    def test_paper_default_has_correct_data_rates(self) -> None:
        config = CampaignConfig.paper_default()
        self.assertEqual(config.horizontal_data_rate_mbps, 30.0)
        self.assertEqual(config.vertical_data_rate_mbps, 10.0)

    def test_paper_default_has_bounded_smoke_episode_counts(self) -> None:
        config = CampaignConfig.paper_default()
        self.assertEqual(config.readiness_probe_episode_count, 3)
        self.assertEqual(config.readiness_probe_episode_length, 50)
        self.assertEqual(config.pilot_episode_length, 50)
        self.assertEqual(config.evaluation_episode_length, 50)
        self.assertEqual(config.full_campaign_episode_length, 110)

    def test_paper_default_has_correct_campaign_flags(self) -> None:
        config = CampaignConfig.paper_default()
        self.assertFalse(config.full_campaign_enabled)
        self.assertTrue(config.readiness_manual_approval_required)
        self.assertEqual(config.readiness_manual_approval_status, "approved")
        self.assertEqual(
            config.readiness_manual_approval_reference,
            "paper-default-smoke-campaign-approved",
        )

    def test_paper_default_has_correct_pilot_budget(self) -> None:
        config = CampaignConfig.paper_default()
        self.assertEqual(config.pilot_budget.primary_episodes, 10)
        self.assertEqual(config.pilot_budget.follow_up_episodes, 25)

    def test_paper_default_passes_post_init_validation(self) -> None:
        # Should not raise
        config = CampaignConfig.paper_default()
        self.assertIsInstance(config, CampaignConfig)

    def test_paper_default_has_correct_feature_id(self) -> None:
        config = CampaignConfig.paper_default()
        self.assertEqual(
            config.feature_id, "041-full-training-reproduction-campaign"
        )


if __name__ == "__main__":
    unittest.main()