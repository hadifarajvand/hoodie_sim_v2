from __future__ import annotations

import unittest

from src.analysis.paper_hoodie_network_implementation import PaperHoodieNetworkConfig


class PaperHoodieNetworkConfigUnitTests(unittest.TestCase):
    def test_network_config_separates_q_and_lstm_layers(self) -> None:
        config = PaperHoodieNetworkConfig.standard()
        self.assertEqual(config.q_network_hidden_layers, [1024, 1024, 1024])
        self.assertEqual(config.lstm_num_layers, 1)
        self.assertEqual(config.lstm_hidden_size, 20)
        self.assertEqual(config.lstm_lookback_w, 10)
        self.assertEqual(config.action_count, 3)
        self.assertEqual(config.state_dim, 3)

    def test_network_config_rejects_sloppy_n_l_coupling(self) -> None:
        with self.assertRaises(ValueError):
            PaperHoodieNetworkConfig.from_shared_n_l(shared_n_l=20)

    def test_action_count_matches_feature_038_contract(self) -> None:
        with self.assertRaises(ValueError):
            PaperHoodieNetworkConfig(
                state_dim=None,
                q_network_hidden_layers=[1024, 1024, 1024],
                action_count=4,
                lstm_lookback_w=10,
                lstm_num_layers=1,
                lstm_hidden_size=20,
                model_initialization_seed=19,
            )

    def test_network_config_rejects_missing_q_and_lstm_fields(self) -> None:
        with self.assertRaises(ValueError):
            PaperHoodieNetworkConfig(
                state_dim=None,
                q_network_hidden_layers=None,
                lstm_lookback_w=10,
                lstm_num_layers=1,
                lstm_hidden_size=20,
                model_initialization_seed=19,
            )
        with self.assertRaises(ValueError):
            PaperHoodieNetworkConfig(
                state_dim=None,
                q_network_hidden_layers=[1024, 1024, 1024],
                lstm_lookback_w=10,
                lstm_num_layers=None,
                lstm_hidden_size=20,
                model_initialization_seed=19,
            )
        with self.assertRaises(ValueError):
            PaperHoodieNetworkConfig(
                state_dim=None,
                q_network_hidden_layers=[1024, 1024, 1024],
                lstm_lookback_w=10,
                lstm_num_layers=1,
                lstm_hidden_size=None,
                model_initialization_seed=19,
            )

    def test_network_config_rejects_q_width_and_lstm_width_swaps(self) -> None:
        with self.assertRaises(ValueError):
            PaperHoodieNetworkConfig(
                state_dim=None,
                q_network_hidden_layers=[20],
                lstm_lookback_w=10,
                lstm_num_layers=1,
                lstm_hidden_size=20,
                model_initialization_seed=19,
            )
        with self.assertRaises(ValueError):
            PaperHoodieNetworkConfig(
                state_dim=None,
                q_network_hidden_layers=20,
                lstm_lookback_w=10,
                lstm_num_layers=1,
                lstm_hidden_size=20,
                model_initialization_seed=19,
            )
        with self.assertRaises(ValueError):
            PaperHoodieNetworkConfig(
                state_dim=None,
                q_network_hidden_layers=[1024, 1024, 1024],
                lstm_lookback_w=10,
                lstm_num_layers=1,
                lstm_hidden_size=1024,
                model_initialization_seed=19,
            )


if __name__ == "__main__":
    unittest.main()
