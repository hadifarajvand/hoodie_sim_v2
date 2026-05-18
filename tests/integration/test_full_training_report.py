from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.full_training_reproduction_campaign import CampaignConfig, build_campaign_prerequisite_tags_verified, generate_campaign_artifacts, run_campaign


class FullTrainingReportIntegrationTests(unittest.TestCase):
    def _config(self) -> CampaignConfig:
        return CampaignConfig(
            readiness_probe_episode_count=1,
            readiness_probe_episode_length=5,
            pilot_episode_length=10,
            evaluation_episode_length=10,
        )

    def test_campaign_report_schema(self) -> None:
        result = run_campaign(self._config(), stage="readiness_probe", episodes=10, enable_full_campaign=False)
        payload = result.training_report.to_dict()
        required_keys = {
            "feature_id",
            "prerequisite_tags_verified",
            "prior_feature_gates_verified",
            "target_update_unit_decision",
            "terminal_exposure_gate",
            "campaign_stage",
            "campaign_config",
            "runtime_contracts_verified",
            "environment_interface_verified",
            "network_contract_verified",
            "replay_contract_verified",
            "delayed_reward_contract_verified",
            "seed_protocol_verified",
            "train_eval_split_verified",
            "checkpoint_schema_verified",
            "training_execution_summary",
            "evaluation_summary",
            "baseline_reference_summary",
            "reproduction_claim_status",
            "no_curve_fitting",
            "no_simulator_output_tuning",
            "no_dependency_drift",
            "no_environment_contract_drift",
            "no_policy_drift",
            "no_reward_timing_change",
            "final_verdict",
        }
        self.assertTrue(required_keys.issubset(payload))
        self.assertEqual(payload["feature_id"], "041-full-training-reproduction-campaign")
        self.assertEqual(payload["campaign_stage"], "readiness_probe")
        self.assertEqual(payload["target_update_unit_decision"]["target_update_unit"], "optimizer_step")
        self.assertTrue(payload["no_curve_fitting"])
        self.assertTrue(payload["no_simulator_output_tuning"])
        self.assertTrue(payload["no_dependency_drift"])
        self.assertTrue(payload["no_environment_contract_drift"])
        self.assertTrue(payload["no_policy_drift"])
        self.assertTrue(payload["no_reward_timing_change"])
        self.assertFalse(payload["reproduction_claim_status"]["automatic_claim"])
        self.assertEqual(payload["reproduction_claim_status"]["status"], "no_claim")
        self.assertFalse(payload["training_execution_summary"]["full_campaign_executed"])
        self.assertFalse(payload["training_execution_summary"]["pilot_training_executed"])
        self.assertEqual(payload["training_execution_summary"]["optimizer_step_count"], 0)
        self.assertEqual(payload["training_execution_summary"]["replay_size"], 0)
        self.assertIsNotNone(payload["training_execution_summary"]["full_campaign_block_reason"])
        self.assertEqual(payload["terminal_exposure_gate"]["readiness_manual_approval_status"], "not_approved")
        self.assertEqual(payload["terminal_exposure_gate"]["readiness_manual_approval_required"], True)
        self.assertEqual(payload["terminal_exposure_gate"]["readiness_block_reason"], "zero_reward_bearing_terminal_transitions")

    def test_campaign_report_artifacts_are_written(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "artifacts/analysis/full-training-reproduction-campaign"
            result = generate_campaign_artifacts(
                self._config(),
                stage="pilot_training",
                episodes=10,
                enable_full_campaign=False,
                output_dir=output_dir,
            )
            readiness_json = output_dir / "campaign-readiness-report.json"
            readiness_md = output_dir / "campaign-readiness-report.md"
            training_json = output_dir / "training-campaign-report.json"
            training_md = output_dir / "training-campaign-report.md"
            self.assertTrue(readiness_json.exists())
            self.assertTrue(readiness_md.exists())
            self.assertTrue(training_json.exists())
            self.assertTrue(training_md.exists())
            payload = json.loads(training_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["feature_id"], "041-full-training-reproduction-campaign")
            self.assertEqual(payload["campaign_stage"], "readiness_probe")
            self.assertEqual(payload["final_verdict"], "readiness_blocked_terminal_exposure")
            self.assertTrue(result.training_report.no_curve_fitting)
            self.assertIsNone(result.checkpoint_path)
            self.assertEqual(result.training_report.training_execution_summary["pilot_training_executed"], False)
            self.assertEqual(result.training_report.training_execution_summary["optimizer_step_count"], 0)
            self.assertEqual(result.training_report.training_execution_summary["replay_size"], 0)
            self.assertEqual(
                result.training_report.checkpoint_schema_verified["optimizer_step_count"],
                0,
            )
            self.assertFalse(
                Path("artifacts/checkpoints/full-training-reproduction-campaign/pilot_training-checkpoint-metadata.json").exists()
            )

    def test_no_curve_fitting_or_reproduction_claim(self) -> None:
        result = run_campaign(self._config(), stage="readiness_probe", episodes=10, enable_full_campaign=False)
        self.assertTrue(result.training_report.no_curve_fitting)
        self.assertTrue(result.training_report.no_simulator_output_tuning)
        self.assertFalse(result.training_report.reproduction_claim_status["automatic_claim"])
        self.assertEqual(result.training_report.reproduction_claim_status["status"], "no_claim")

    def test_prerequisite_tags_allow_only_local_specify_pointer_dirty_file(self) -> None:
        tags = build_campaign_prerequisite_tags_verified()
        no_unrelated_dirty_files = next(item for item in tags if item["name"] == "no_unrelated_dirty_files")
        self.assertTrue(no_unrelated_dirty_files["verified"])


if __name__ == "__main__":
    unittest.main()
