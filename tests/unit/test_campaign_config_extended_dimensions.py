from __future__ import annotations

import unittest

from src.analysis.full_training_reproduction_campaign import CampaignConfig
from src.analysis.paper_hoodie_network_implementation import PaperHoodieNetworkConfig

PAPER_STATE_DIM = 74
PAPER_ACTION_COUNT = 22


class CampaignConfigExtendedDimensionsTests(unittest.TestCase):
    def test_campaign_config_accepts_paper_state_dim_and_action_count(self) -> None:
        config = CampaignConfig(state_dim=PAPER_STATE_DIM, action_count=PAPER_ACTION_COUNT)
        self.assertEqual(config.state_dim, PAPER_STATE_DIM)
        self.assertEqual(config.action_count, PAPER_ACTION_COUNT)

    def test_campaign_config_builds_network_config_with_correct_action_count(self) -> None:
        config = CampaignConfig(state_dim=PAPER_STATE_DIM, action_count=PAPER_ACTION_COUNT)
        network_config = config.build_network_config()
        self.assertEqual(network_config.state_dim, PAPER_STATE_DIM)
        self.assertEqual(network_config.action_count, PAPER_ACTION_COUNT)

    def test_campaign_config_rejects_non_positive_state_dim(self) -> None:
        with self.assertRaises(ValueError):
            CampaignConfig(state_dim=0)
        with self.assertRaises(ValueError):
            CampaignConfig(state_dim=-1)

    def test_campaign_config_rejects_non_positive_action_count(self) -> None:
        with self.assertRaises(ValueError):
            CampaignConfig(action_count=0)
        with self.assertRaises(ValueError):
            CampaignConfig(action_count=-1)

    def test_campaign_config_defaults_still_accepted(self) -> None:
        config = CampaignConfig()
        self.assertEqual(config.state_dim, 3)
        self.assertEqual(config.action_count, 3)


class PaperHoodieNetworkConfigExtendedDimensionsTests(unittest.TestCase):
    def test_paper_hoodie_network_config_accepts_paper_action_count(self) -> None:
        config = PaperHoodieNetworkConfig.standard(
            state_dim=PAPER_STATE_DIM,
            action_count=PAPER_ACTION_COUNT,
            model_initialization_seed=19,
        )
        self.assertEqual(config.state_dim, PAPER_STATE_DIM)
        self.assertEqual(config.action_count, PAPER_ACTION_COUNT)

    def test_paper_hoodie_network_config_rejects_non_positive_action_count(self) -> None:
        with self.assertRaises(ValueError):
            PaperHoodieNetworkConfig.standard(action_count=0)
        with self.assertRaises(ValueError):
            PaperHoodieNetworkConfig.standard(action_count=-1)

    def test_paper_hoodie_network_config_rejects_non_positive_state_dim(self) -> None:
        with self.assertRaises(ValueError):
            PaperHoodieNetworkConfig.standard(state_dim=0)
        with self.assertRaises(ValueError):
            PaperHoodieNetworkConfig.standard(state_dim=-1)

    def test_paper_hoodie_network_config_defaults_still_accepted(self) -> None:
        config = PaperHoodieNetworkConfig.standard()
        self.assertEqual(config.state_dim, 3)
        self.assertEqual(config.action_count, 3)

    def test_expected_output_shape_is_dynamic(self) -> None:
        config = PaperHoodieNetworkConfig.standard(action_count=PAPER_ACTION_COUNT)
        self.assertEqual(config.expected_output_shape, f"batch_size x {PAPER_ACTION_COUNT}")


class BuildNetworkConfigIntegrationTests(unittest.TestCase):
    def test_build_network_config_passes_state_dim_and_action_count(self) -> None:
        campaign_config = CampaignConfig(state_dim=PAPER_STATE_DIM, action_count=PAPER_ACTION_COUNT)
        network_config = campaign_config.build_network_config()
        self.assertEqual(network_config.state_dim, PAPER_STATE_DIM)
        self.assertEqual(network_config.action_count, PAPER_ACTION_COUNT)
        self.assertEqual(network_config.q_network_hidden_layers, [1024, 1024, 1024])
        self.assertEqual(network_config.lstm_num_layers, 1)
        self.assertEqual(network_config.lstm_hidden_size, 20)


if __name__ == "__main__":
    unittest.main()
