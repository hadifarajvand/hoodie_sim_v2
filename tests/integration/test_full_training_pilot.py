from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.analysis.full_training_reproduction_campaign import CampaignConfig, ReadinessProbeResult, generate_campaign_artifacts, run_campaign


def _approved_readiness_result(config: CampaignConfig) -> ReadinessProbeResult:
    return ReadinessProbeResult(
        campaign_stage="readiness_probe",
        gate_status="pilot-ready",
        probe_episode_count=1,
        probe_step_count=1,
        generated_task_count=1,
        transition_count=1,
        completed_task_count=1,
        dropped_task_count=0,
        pending_at_horizon_count=0,
        terminal_transition_count=1,
        reward_bearing_transition_count=1,
        non_terminal_transition_count=0,
        terminal_transition_ratio=1.0,
        reward_bearing_transition_ratio=1.0,
        pending_at_horizon_ratio=0.0,
        illegal_action_count=0,
        illegal_action_ratio=0.0,
        action_count_by_type={"local": 1},
        local_action_count=1,
        horizontal_action_count=0,
        vertical_action_count=0,
        readiness_manual_approval_required=True,
        readiness_manual_approval_status="approved",
        readiness_block_reason=None,
        target_update_unit=config.target_update_contract.target_update_unit,
    )


class FullTrainingPilotIntegrationTests(unittest.TestCase):
    def _approved_fast_config(self) -> CampaignConfig:
        return CampaignConfig(
            readiness_manual_approval_status="approved",
            readiness_manual_approval_reference="user-approval-041",
            readiness_probe_episode_count=1,
            readiness_probe_episode_length=5,
            pilot_episode_length=10,
            evaluation_episode_length=10,
        )

    def test_training_loop_uses_hoodie_gym_environment(self) -> None:
        config = self._approved_fast_config()
        with patch("src.analysis.full_training_reproduction_campaign.runner.CampaignReadinessProbe.run", return_value=_approved_readiness_result(config)):
            result = run_campaign(config, stage="pilot_training", episodes=10, enable_full_campaign=False)
        self.assertEqual(result.training_report.environment_interface_verified["uses_HoodieGymEnvironment"], True)
        self.assertEqual(result.training_report.environment_interface_verified["live_rollouts_only"], True)

    def test_training_loop_emits_legal_actions_only(self) -> None:
        config = self._approved_fast_config()
        with patch("src.analysis.full_training_reproduction_campaign.runner.CampaignReadinessProbe.run", return_value=_approved_readiness_result(config)):
            result = run_campaign(config, stage="pilot_training", episodes=10, enable_full_campaign=False)
        self.assertTrue(result.training_report.training_execution_summary["legal_action_only"])
        self.assertEqual(result.training_report.training_execution_summary["full_campaign_executed"], False)
        self.assertTrue(result.training_report.training_execution_summary["pilot_training_executed"])

    def test_ddqn_loss_is_finite_in_pilot(self) -> None:
        config = self._approved_fast_config()
        with patch("src.analysis.full_training_reproduction_campaign.runner.CampaignReadinessProbe.run", return_value=_approved_readiness_result(config)):
            result = run_campaign(config, stage="pilot_training", episodes=10, enable_full_campaign=False)
        summary = result.training_report.training_execution_summary
        self.assertTrue(summary["loss_is_finite"])
        self.assertGreater(summary["optimizer_step_count"], 0)

    def test_target_update_schedule_uses_approved_unit_only(self) -> None:
        config = self._approved_fast_config()
        with patch("src.analysis.full_training_reproduction_campaign.runner.CampaignReadinessProbe.run", return_value=_approved_readiness_result(config)):
            result = run_campaign(config, stage="pilot_training", episodes=10, enable_full_campaign=False)
        checkpoint = result.training_report.checkpoint_schema_verified
        self.assertEqual(checkpoint["target_update_unit"], "optimizer_step")
        self.assertEqual(result.training_report.target_update_unit_decision["target_update_unit"], "optimizer_step")
        self.assertEqual(result.training_report.training_execution_summary["target_sync_count"], 0)

    def test_checkpoint_metadata_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = self._approved_fast_config()
            with patch("src.analysis.full_training_reproduction_campaign.runner.CampaignReadinessProbe.run", return_value=_approved_readiness_result(config)):
                result = generate_campaign_artifacts(
                    config,
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
