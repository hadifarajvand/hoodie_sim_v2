from __future__ import annotations

import unittest

from src.analysis.smoke_training import SmokeTrainingConfig, build_smoke_batch


class SmokeTrainingContractUnitTests(unittest.TestCase):
    def test_smoke_training_config_is_tiny_and_deterministic(self) -> None:
        config = SmokeTrainingConfig()
        self.assertEqual(config.feature_id, "040-smoke-training")
        self.assertEqual(config.state_dim, 3)
        self.assertEqual(config.action_count, 3)
        self.assertEqual(config.lookback_w, 10)
        self.assertEqual(config.batch_size, 2)
        self.assertEqual(config.optimizer_steps, 1)
        self.assertEqual(config.model_initialization_seed, 19)
        self.assertEqual(config.smoke_seed, 40)
        self.assertEqual(config.seed_bundle.signature, "smoke=40|python=40|torch=40|model=19")

    def test_smoke_batch_obeys_replay_and_delayed_reward_contract(self) -> None:
        config = SmokeTrainingConfig()
        batch = build_smoke_batch(config)
        self.assertEqual(tuple(batch.state_tensor.shape), (2, 10, 3))
        self.assertEqual(tuple(batch.next_state_tensor.shape), (2, 10, 3))
        self.assertEqual(tuple(batch.action_index_tensor.tolist()), (1, 2))
        self.assertEqual(tuple(batch.legal_action_mask_tensor.shape), (2, 3))
        self.assertTrue(batch.reward_available_tensor.tolist()[1])
        self.assertFalse(batch.reward_available_tensor.tolist()[0])
        self.assertTrue(batch.transitions[0].pending_at_horizon)
        self.assertFalse(batch.transitions[0].is_terminal)
        self.assertTrue(batch.transitions[1].is_terminal)
        self.assertEqual(batch.summary.data_source, "smoke_fixture")
        self.assertEqual(batch.transitions[0].data_source, "smoke_fixture")
        self.assertEqual(batch.transitions[1].data_source, "smoke_fixture")
        self.assertTrue(all(action in {0, 1, 2} for action in batch.action_index_tensor.tolist()))

    def test_smoke_training_runs_one_optimizer_step(self) -> None:
        from src.analysis.smoke_training import run_smoke_training

        report = run_smoke_training(SmokeTrainingConfig())
        self.assertEqual(report.optimizer_step_summary["optimizer_step_count"], 1)
        self.assertTrue(report.no_target_update_execution)
        self.assertTrue(report.no_full_training)
        self.assertTrue(report.no_campaign_execution)

    def test_smoke_loss_is_finite(self) -> None:
        from src.analysis.smoke_training import run_smoke_training

        report = run_smoke_training(SmokeTrainingConfig())
        self.assertTrue(report.loss_summary["is_finite"])
        self.assertTrue(report.loss_summary["loss_value"] == report.loss_summary["loss_value"])

    def test_online_parameters_change_after_smoke_step(self) -> None:
        from src.analysis.smoke_training import run_smoke_training

        report = run_smoke_training(SmokeTrainingConfig())
        self.assertGreater(report.parameter_update_summary["changed_parameter_count"], 0)
        self.assertGreater(len(report.parameter_update_summary["changed_parameter_names"]), 0)

    def test_target_network_is_not_updated(self) -> None:
        from src.analysis.smoke_training import run_smoke_training

        report = run_smoke_training(SmokeTrainingConfig())
        self.assertFalse(report.optimizer_step_summary["target_update_executed"])
        self.assertFalse(report.parameter_update_summary["target_parameters_changed"])

    def test_no_paper_reproduction_or_campaign_claim(self) -> None:
        from src.analysis.smoke_training import run_smoke_training

        report = run_smoke_training(SmokeTrainingConfig())
        self.assertTrue(report.no_paper_reproduction_claim)
        self.assertTrue(report.no_curve_fitting)
        self.assertTrue(report.no_campaign_execution)
        self.assertTrue(report.no_baseline_comparison)
        self.assertTrue(report.feature_038_training_readiness_block_respected)

    def test_no_dependency_environment_policy_reward_drift(self) -> None:
        from src.analysis.smoke_training import run_smoke_training

        report = run_smoke_training(SmokeTrainingConfig())
        self.assertTrue(report.no_dependency_drift)
        self.assertTrue(report.no_environment_contract_drift)
        self.assertTrue(report.no_policy_drift)
        self.assertTrue(report.no_reward_timing_change)


if __name__ == "__main__":
    unittest.main()
