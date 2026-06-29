from __future__ import annotations

import unittest

import torch

from src.analysis.full_training_reproduction_campaign import CampaignConfig
from src.analysis.full_training_reproduction_campaign.replay import PAPER_ACTION_COUNT, PAPER_STATE_DIM
from src.analysis.full_training_reproduction_campaign.trainer import CampaignPolicy, DDQNTrainer
from src.analysis.paper_hoodie_network_implementation import PaperHoodieNetworkConfig, build_online_network


class PaperNetworkActionCount22Tests(unittest.TestCase):
    def test_network_accepts_action_count_22(self) -> None:
        config = PaperHoodieNetworkConfig.standard(state_dim=PAPER_STATE_DIM, action_count=PAPER_ACTION_COUNT)
        network = build_online_network(config)
        self.assertEqual(network.action_count, PAPER_ACTION_COUNT)

    def test_network_output_shape_is_22(self) -> None:
        config = PaperHoodieNetworkConfig.standard(state_dim=PAPER_STATE_DIM, action_count=PAPER_ACTION_COUNT)
        network = build_online_network(config)
        sample_input = torch.zeros((2, 10, PAPER_STATE_DIM), dtype=torch.float32)
        with torch.no_grad():
            output = network(sample_input)
        self.assertEqual(output.shape, (2, PAPER_ACTION_COUNT))

    def test_network_still_accepts_action_count_3(self) -> None:
        config = PaperHoodieNetworkConfig.standard(state_dim=3, action_count=3)
        network = build_online_network(config)
        self.assertEqual(network.action_count, 3)

    def test_network_rejects_invalid_action_count(self) -> None:
        with self.assertRaises(ValueError):
            PaperHoodieNetworkConfig.standard(state_dim=3, action_count=0)
        with self.assertRaises(ValueError):
            build_online_network(PaperHoodieNetworkConfig.standard(state_dim=3, action_count=5))

    def test_advantage_head_width_matches_action_count(self) -> None:
        config = PaperHoodieNetworkConfig.standard(state_dim=PAPER_STATE_DIM, action_count=PAPER_ACTION_COUNT)
        network = build_online_network(config)
        self.assertEqual(network.advantage_head.out_features, PAPER_ACTION_COUNT)


class DDQNTrainerPaperInstantiationTests(unittest.TestCase):
    def test_ddqn_trainer_instantiates_with_74_22(self) -> None:
        config = CampaignConfig(state_dim=PAPER_STATE_DIM, action_count=PAPER_ACTION_COUNT)
        trainer = DDQNTrainer(config)
        self.assertEqual(trainer.config.state_dim, PAPER_STATE_DIM)
        self.assertEqual(trainer.config.action_count, PAPER_ACTION_COUNT)
        self.assertEqual(trainer.online_network.action_count, PAPER_ACTION_COUNT)
        self.assertEqual(trainer.target_network.action_count, PAPER_ACTION_COUNT)

    def test_ddqn_trainer_legacy_still_works(self) -> None:
        config = CampaignConfig()
        trainer = DDQNTrainer(config)
        self.assertEqual(trainer.config.action_count, 3)
        self.assertEqual(trainer.online_network.action_count, 3)


class CampaignPolicy22ActionMaskTests(unittest.TestCase):
    def _make_policy(self, action_count: int = PAPER_ACTION_COUNT, state_dim: int = PAPER_STATE_DIM) -> CampaignPolicy:
        config = PaperHoodieNetworkConfig.standard(state_dim=state_dim, action_count=action_count)
        network = build_online_network(config)
        return CampaignPolicy(network, action_count=action_count)

    def test_paper_policy_mask_shape_matches_q_values(self) -> None:
        policy = self._make_policy(PAPER_ACTION_COUNT)
        state_window = torch.zeros((10, PAPER_STATE_DIM), dtype=torch.float32)
        mask_22 = {"legal_action_mask": [True] * PAPER_ACTION_COUNT}
        with torch.no_grad():
            q_values = policy.network(state_window.unsqueeze(0))[0]
        self.assertEqual(q_values.shape[0], PAPER_ACTION_COUNT)
        idx = policy.choose_action_index(state_window, mask_22)
        self.assertIsInstance(idx, int)
        self.assertTrue(0 <= idx < PAPER_ACTION_COUNT)

    def test_paper_policy_maps_local_correctly(self) -> None:
        policy = self._make_policy(PAPER_ACTION_COUNT)
        state_window = torch.zeros((10, PAPER_STATE_DIM), dtype=torch.float32)
        mask_only_local = {"legal_action_mask": [i == 0 for i in range(PAPER_ACTION_COUNT)]}
        action = policy.choose_action(state_window, mask_only_local)
        self.assertEqual(action, "local")

    def test_paper_policy_maps_cloud_correctly(self) -> None:
        policy = self._make_policy(PAPER_ACTION_COUNT)
        state_window = torch.zeros((10, PAPER_STATE_DIM), dtype=torch.float32)
        mask_only_cloud = {"legal_action_mask": [i == 21 for i in range(PAPER_ACTION_COUNT)]}
        action = policy.choose_action(state_window, mask_only_cloud)
        self.assertEqual(action, "cloud")

    def test_legacy_policy_3_actions_still_works(self) -> None:
        policy = self._make_policy(3, state_dim=3)
        state_window = torch.zeros((10, 3), dtype=torch.float32)
        mask = {"local": True, "horizontal": True, "vertical": True}
        with torch.no_grad():
            q_values = policy.network(state_window.unsqueeze(0))[0]
        self.assertEqual(q_values.shape[0], 3)
        idx = policy.choose_action_index(state_window, mask)
        self.assertTrue(0 <= idx < 3)
        action = policy.choose_action(state_window, mask)
        self.assertIn(action, {"local", "horizontal", "vertical"})


if __name__ == "__main__":
    unittest.main()
