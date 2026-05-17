from __future__ import annotations

import unittest

from src.analysis.paper_hoodie_network_implementation import PaperHoodieNetworkConfig, build_network_implementation_report


class PaperHoodieNetworkShapeTests(unittest.TestCase):
    def test_lstm_forward_accepts_lookback_w_10(self) -> None:
        config = PaperHoodieNetworkConfig.standard()
        self.assertEqual(config.expected_input_shape, "batch_size x 10 x state_dim")
        self.assertEqual(config.lstm_lookback_w, 10)

    def test_dueling_network_outputs_batch_by_action_count(self) -> None:
        config = PaperHoodieNetworkConfig.standard()
        self.assertEqual(config.expected_output_shape, "batch_size x 3")
        self.assertEqual(config.action_count, 3)

    def test_dueling_q_aggregation_shape(self) -> None:
        report = build_network_implementation_report()
        self.assertEqual(report.shape_validation_summary["dueling_heads_contract"]["aggregation_rule"], "Q(s,a) = V(s) + A(s,a) - mean_a A(s,a)")
        self.assertEqual(report.shape_validation_summary["expected_output_shape"], "batch_size x 3")

    def test_online_target_networks_are_architecture_compatible(self) -> None:
        report = build_network_implementation_report()
        pair = report.shape_validation_summary["online_target_pair_contract"]
        self.assertEqual(pair["forward_api_shape"], "batch_size x 3")
        self.assertFalse(pair["compatibility_verified"])

    def test_deterministic_initialization_with_model_seed(self) -> None:
        config = PaperHoodieNetworkConfig.standard(model_initialization_seed=19)
        self.assertEqual(config.model_initialization_seed, 19)
        report = build_network_implementation_report()
        self.assertEqual(report.architecture_config["model_initialization_seed"], 19)
        self.assertFalse(report.deterministic_initialization_verified)

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
