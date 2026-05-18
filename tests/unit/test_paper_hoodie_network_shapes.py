from __future__ import annotations

import unittest

import torch

from src.analysis.paper_hoodie_network_implementation import (
    PaperHoodieNetworkConfig,
    build_network_implementation_report,
    build_online_network,
    build_target_network,
)


class PaperHoodieNetworkShapeTests(unittest.TestCase):
    def _config(self) -> PaperHoodieNetworkConfig:
        return PaperHoodieNetworkConfig.standard(state_dim=3, model_initialization_seed=19)

    def _sample_input(self) -> torch.Tensor:
        config = self._config()
        return torch.zeros((2, config.lstm_lookback_w, config.state_dim), dtype=torch.float32)

    def test_lstm_forward_accepts_lookback_w_10(self) -> None:
        config = self._config()
        model = build_online_network(config)
        output = model(self._sample_input())
        self.assertEqual(tuple(output.shape), (2, 3))
        self.assertEqual(config.expected_input_shape, "batch_size x 10 x state_dim")
        self.assertEqual(config.lstm_lookback_w, 10)

    def test_dueling_network_outputs_batch_by_action_count(self) -> None:
        config = self._config()
        model = build_online_network(config)
        value, advantage, q_values = model.forward_components(self._sample_input())
        self.assertEqual(tuple(q_values.shape), (2, 3))
        self.assertEqual(tuple(value.shape), (2, 1))
        self.assertEqual(tuple(advantage.shape), (2, 3))
        self.assertEqual(config.expected_output_shape, "batch_size x 3")
        self.assertEqual(config.action_count, 3)

    def test_dueling_q_aggregation_shape(self) -> None:
        config = self._config()
        model = build_online_network(config)
        value, advantage, q_values = model.forward_components(self._sample_input())
        expected = value + advantage - advantage.mean(dim=-1, keepdim=True)
        self.assertTrue(torch.allclose(q_values, expected))
        self.assertEqual(tuple(q_values.shape), (2, 3))

    def test_online_target_networks_are_architecture_compatible(self) -> None:
        config = self._config()
        online = build_online_network(config)
        target = build_target_network(config)
        sample = self._sample_input()
        self.assertEqual(online.architecture_signature(), target.architecture_signature())
        self.assertEqual(tuple(online(sample).shape), (2, 3))
        self.assertEqual(tuple(target(sample).shape), (2, 3))
        self.assertTrue(torch.equal(online(sample), target(sample)))

    def test_deterministic_initialization_with_model_seed(self) -> None:
        config = self._config()
        first = build_online_network(config)
        second = build_online_network(config)
        sample = self._sample_input()
        self.assertEqual(config.model_initialization_seed, 19)
        self.assertEqual(first.architecture_signature(), second.architecture_signature())
        for first_param, second_param in zip(first.state_dict().values(), second.state_dict().values()):
            self.assertTrue(torch.equal(first_param, second_param))
        self.assertTrue(torch.equal(first(sample), second(sample)))

    def test_no_training_optimizer_replay_execution_added(self) -> None:
        report = build_network_implementation_report()
        self.assertTrue(report.no_training_started)
        self.assertTrue(report.no_optimizer_step)
        self.assertTrue(report.no_replay_execution)
        self.assertTrue(report.no_target_update_execution)

    def test_no_dependency_environment_policy_reward_drift(self) -> None:
        report = build_network_implementation_report()
        self.assertTrue(report.no_dependency_drift)
        self.assertTrue(report.no_environment_contract_drift)
        self.assertTrue(report.no_policy_drift)
        self.assertTrue(report.no_reward_timing_change)


if __name__ == "__main__":
    unittest.main()
