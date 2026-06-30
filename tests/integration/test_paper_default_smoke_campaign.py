from __future__ import annotations

import math
import unittest

from src.analysis.full_training_reproduction_campaign import CampaignConfig
from src.analysis.full_training_reproduction_campaign.trainer import DDQNTrainer


class PaperDefaultSmokeCampaignIntegrationTests(unittest.TestCase):
    def test_paper_default_config_loads(self) -> None:
        config = CampaignConfig.paper_default()
        self.assertEqual(config.state_dim, 74)
        self.assertEqual(config.action_count, 22)

    def test_ddqn_trainer_instantiates_with_paper_default(self) -> None:
        config = CampaignConfig.paper_default()
        trainer = DDQNTrainer(config)
        self.assertEqual(trainer.config.state_dim, 74)
        self.assertEqual(trainer.config.action_count, 22)
        self.assertEqual(trainer.policy.action_count, 22)

    def test_paper_state_builder_rows_used(self) -> None:
        config = CampaignConfig.paper_default()
        trainer = DDQNTrainer(config)
        self.assertEqual(trainer.state_builder.num_eas, trainer.num_eas)
        state = trainer.state_builder.build_state(
            task_size=1.0,
            processing_density=0.5,
            private_wait_time=0.0,
            offload_wait_time=0.0,
            public_queue_lengths=[0.0] * trainer.num_eas,
            load_forecast=[0.0] * trainer.num_eas,
        )
        self.assertEqual(state.shape[0], 74)

    def test_smoke_episode_runs_without_crash(self) -> None:
        config = CampaignConfig.paper_default()
        trainer = DDQNTrainer(config)
        summary = trainer._episode_rollout(
            episode_id=0,
            seed=config.seed_bundle.training_trace_generation_seed,
            episode_length=50,
            training=False,
        )
        self.assertIsInstance(summary, dict)
        self.assertGreaterEqual(summary["transition_count"], 0)

    def test_smoke_does_not_trigger_full_training(self) -> None:
        config = CampaignConfig.paper_default()
        self.assertFalse(config.full_campaign_enabled)

    def test_smoke_episode_no_nan_loss(self) -> None:
        config = CampaignConfig.paper_default()
        trainer = DDQNTrainer(config)
        summary = trainer._episode_rollout(
            episode_id=0,
            seed=config.seed_bundle.training_trace_generation_seed,
            episode_length=50,
            training=True,
        )
        for loss_val in summary["loss_values"]:
            self.assertFalse(math.isnan(loss_val), f"NaN loss: {loss_val}")
            self.assertFalse(math.isinf(loss_val), f"Inf loss: {loss_val}")

    def test_legacy_3d_config_unchanged(self) -> None:
        legacy = CampaignConfig()
        self.assertEqual(legacy.state_dim, 3)
        self.assertEqual(legacy.action_count, 3)
        self.assertEqual(legacy.pilot_episode_length, 20)
        self.assertEqual(legacy.evaluation_episode_length, 110)
        self.assertFalse(legacy.full_campaign_enabled)


if __name__ == "__main__":
    unittest.main()
