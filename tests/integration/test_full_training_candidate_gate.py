from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.analysis.full_training_reproduction_campaign import (
    CampaignCheckpointMetadata,
    CampaignConfig,
    EvaluationSummary,
    PilotTrainingResult,
    ReadinessProbeResult,
    run_campaign,
)


def _successful_pilot_result(config: CampaignConfig) -> PilotTrainingResult:
    checkpoint = CampaignCheckpointMetadata(
        stage="pilot_training",
        feature_id=config.feature_id,
        seed_bundle=config.seed_bundle.to_dict(),
        target_update_unit=config.target_update_contract.target_update_unit,
        config_hash="pilot",
        train_trace_bank_id=config.training_trace_bank_id,
        eval_trace_bank_id=config.evaluation_trace_bank_id,
        optimizer_step_count=1,
        replay_size=64,
        full_campaign_enabled=config.full_campaign_enabled,
    )
    evaluation_summary = EvaluationSummary(
        evaluation_episode_count=1,
        mean_reward=0.0,
        completed_task_count=0,
        dropped_task_count=0,
        terminal_transition_count=0,
        reward_bearing_transition_count=0,
        trace_bank_disjoint=True,
        trace_bank_ids={
            "training": config.training_trace_bank_id,
            "evaluation": config.evaluation_trace_bank_id,
        },
        trace_ids=["eval-0"],
        evaluation_on_training_traces=False,
        candidate_reproduction_supported=False,
    )
    return PilotTrainingResult(
        stage="pilot_training",
        episodes_requested=10,
        episodes_completed=10,
        optimizer_step_count=1,
        target_sync_count=0,
        replay_size=64,
        loss_value=0.123,
        loss_is_finite=True,
        legal_action_only=True,
        delayed_reward_contract_preserved=True,
        pending_at_horizon_preserved=True,
        checkpoint_schema_valid=True,
        train_eval_trace_banks_disjoint=True,
        pilot_training_executed=True,
        full_campaign_executed=False,
        full_campaign_block_reason="pilot only",
        evaluation_summary=evaluation_summary.to_dict(),
        checkpoint_metadata=checkpoint,
    )


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


class FullTrainingCandidateGateIntegrationTests(unittest.TestCase):
    def _pending_config(self) -> CampaignConfig:
        return CampaignConfig(
            readiness_manual_approval_status="not_approved",
            readiness_probe_episode_count=1,
            readiness_probe_episode_length=5,
            pilot_episode_length=10,
            evaluation_episode_length=10,
        )

    def _approved_config(self) -> CampaignConfig:
        return CampaignConfig(
            readiness_manual_approval_status="approved",
            readiness_manual_approval_reference="user-approval-041",
            readiness_probe_episode_count=1,
            readiness_probe_episode_length=5,
            pilot_episode_length=10,
            evaluation_episode_length=10,
        )

    def test_full_campaign_blocked_before_readiness_and_pilot(self) -> None:
        blocked_result = run_campaign(self._pending_config(), stage="full_training_candidate", episodes=10, enable_full_campaign=True)
        self.assertEqual(blocked_result.full_campaign_block_reason, "zero_reward_bearing_terminal_transitions")
        self.assertEqual(blocked_result.training_report.campaign_stage, "readiness_probe")
        self.assertFalse(blocked_result.training_report.training_execution_summary["full_campaign_executed"])
        self.assertFalse(blocked_result.training_report.training_execution_summary["pilot_training_executed"])
        self.assertEqual(blocked_result.training_report.training_execution_summary["optimizer_step_count"], 0)
        self.assertEqual(blocked_result.training_report.training_execution_summary["replay_size"], 0)

        approved_config = self._approved_config()
        with patch("src.analysis.full_training_reproduction_campaign.runner.CampaignReadinessProbe.run", return_value=_approved_readiness_result(approved_config)):
            with patch("src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer.run_pilot", return_value=_successful_pilot_result(approved_config)):
                with patch("src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer.evaluate", return_value=EvaluationSummary(
                evaluation_episode_count=1,
                mean_reward=0.0,
                completed_task_count=0,
                dropped_task_count=0,
                terminal_transition_count=0,
                reward_bearing_transition_count=0,
                trace_bank_disjoint=True,
                trace_bank_ids={
                    "training": approved_config.training_trace_bank_id,
                    "evaluation": approved_config.evaluation_trace_bank_id,
                },
                trace_ids=["eval-0"],
                evaluation_on_training_traces=False,
                candidate_reproduction_supported=False,
                )):
                    no_pilot_result = run_campaign(approved_config, stage="full_training_candidate", episodes=10, enable_full_campaign=False)
        self.assertEqual(no_pilot_result.full_campaign_block_reason, "full campaign command/flag not explicitly enabled")
        self.assertEqual(no_pilot_result.training_report.campaign_stage, "pilot_training")
        self.assertFalse(no_pilot_result.training_report.training_execution_summary["full_campaign_executed"])
        self.assertTrue(no_pilot_result.training_report.training_execution_summary["pilot_training_executed"])

    def test_full_campaign_requires_explicit_flag(self) -> None:
        config = self._approved_config()
        with patch("src.analysis.full_training_reproduction_campaign.runner.CampaignReadinessProbe.run", return_value=_approved_readiness_result(config)):
            with patch("src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer.run_pilot", return_value=_successful_pilot_result(config)):
                with patch("src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer.evaluate", return_value=EvaluationSummary(
                evaluation_episode_count=1,
                mean_reward=0.0,
                completed_task_count=0,
                dropped_task_count=0,
                terminal_transition_count=0,
                reward_bearing_transition_count=0,
                trace_bank_disjoint=True,
                trace_bank_ids={
                    "training": config.training_trace_bank_id,
                    "evaluation": config.evaluation_trace_bank_id,
                },
                trace_ids=["eval-0"],
                evaluation_on_training_traces=False,
                candidate_reproduction_supported=False,
                )):
                    result = run_campaign(config, stage="full_training_candidate", episodes=10, enable_full_campaign=False)
        self.assertEqual(result.full_campaign_block_reason, "full campaign command/flag not explicitly enabled")
        self.assertEqual(result.training_report.campaign_stage, "pilot_training")
        self.assertFalse(result.training_report.training_execution_summary["full_campaign_executed"])
        self.assertTrue(result.training_report.training_execution_summary["pilot_training_executed"])

    def test_full_campaign_command_path_is_documented_in_quickstart(self) -> None:
        quickstart = Path("specs/041-full-training-reproduction-campaign/quickstart.md").read_text(encoding="utf-8")
        self.assertIn("--stage full_training_candidate", quickstart)
        self.assertIn("--enable-full-campaign", quickstart)
        self.assertIn("5000", quickstart)


if __name__ == "__main__":
    unittest.main()
