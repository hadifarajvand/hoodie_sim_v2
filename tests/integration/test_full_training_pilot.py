from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.analysis.full_training_reproduction_campaign import CampaignConfig, generate_campaign_artifacts, run_campaign


class FullTrainingPilotIntegrationTests(unittest.TestCase):
    def _approved_fast_config(self) -> CampaignConfig:
        return CampaignConfig(
            readiness_manual_approval_status="approved",
            readiness_probe_episode_count=1,
            readiness_probe_episode_length=5,
            pilot_episode_length=10,
            evaluation_episode_length=10,
        )

    def test_training_loop_uses_hoodie_gym_environment(self) -> None:
        result = run_campaign(self._approved_fast_config(), stage="pilot_training", episodes=10, enable_full_campaign=False)
        self.assertEqual(result.training_report.environment_interface_verified["uses_HoodieGymEnvironment"], True)
        self.assertEqual(result.training_report.environment_interface_verified["live_rollouts_only"], True)

    def test_training_loop_emits_legal_actions_only(self) -> None:
        result = run_campaign(self._approved_fast_config(), stage="pilot_training", episodes=10, enable_full_campaign=False)
        self.assertTrue(result.training_report.training_execution_summary["legal_action_only"])
        self.assertEqual(result.training_report.training_execution_summary["full_campaign_executed"], False)

    def test_ddqn_loss_is_finite_in_pilot(self) -> None:
        result = run_campaign(self._approved_fast_config(), stage="pilot_training", episodes=10, enable_full_campaign=False)
        summary = result.training_report.training_execution_summary
        self.assertTrue(summary["loss_is_finite"])
        self.assertGreater(summary["optimizer_step_count"], 0)

    def test_target_update_schedule_uses_approved_unit_only(self) -> None:
        result = run_campaign(self._approved_fast_config(), stage="pilot_training", episodes=10, enable_full_campaign=False)
        checkpoint = result.training_report.checkpoint_schema_verified
        self.assertEqual(checkpoint["target_update_unit"], "optimizer_step")
        self.assertEqual(result.training_report.target_update_unit_decision["target_update_unit"], "optimizer_step")
        self.assertEqual(result.training_report.training_execution_summary["target_sync_count"], 0)

    def test_checkpoint_metadata_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_campaign_artifacts(
                self._approved_fast_config(),
                stage="pilot_training",
                episodes=10,
                enable_full_campaign=False,
                output_dir=Path(tmpdir) / "artifacts/analysis/full-training-reproduction-campaign",
            )
            self.assertTrue(result.checkpoint_path is not None)
            self.assertTrue(result.checkpoint_path.exists())
            payload = result.checkpoint_path.read_text(encoding="utf-8")
            self.assertIn('"target_update_unit": "optimizer_step"', payload)
            self.assertIn('"stage": "pilot_training"', payload)


if __name__ == "__main__":
    unittest.main()
