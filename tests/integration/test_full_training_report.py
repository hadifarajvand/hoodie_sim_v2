from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.full_training_reproduction_campaign import CampaignConfig, generate_campaign_artifacts, run_campaign


class FullTrainingReportIntegrationTests(unittest.TestCase):
    def _config(self) -> CampaignConfig:
        return CampaignConfig(
            readiness_manual_approval_status="approved",
            readiness_probe_episode_count=1,
            readiness_probe_episode_length=5,
            pilot_episode_length=10,
            evaluation_episode_length=10,
        )

    def test_campaign_report_schema(self) -> None:
        result = run_campaign(self._config(), stage="pilot_training", episodes=10, enable_full_campaign=False)
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
        self.assertEqual(payload["campaign_stage"], "pilot_training")
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
        self.assertIsNotNone(payload["training_execution_summary"]["full_campaign_block_reason"])
        self.assertEqual(payload["terminal_exposure_gate"]["readiness_manual_approval_status"], "approved")
        self.assertEqual(payload["terminal_exposure_gate"]["readiness_manual_approval_required"], True)

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
            self.assertEqual(payload["campaign_stage"], "pilot_training")
            self.assertEqual(payload["final_verdict"], "pilot_training_passed")
            self.assertTrue(result.training_report.no_curve_fitting)

    def test_no_curve_fitting_or_reproduction_claim(self) -> None:
        result = run_campaign(self._config(), stage="pilot_training", episodes=10, enable_full_campaign=False)
        self.assertTrue(result.training_report.no_curve_fitting)
        self.assertTrue(result.training_report.no_simulator_output_tuning)
        self.assertFalse(result.training_report.reproduction_claim_status["automatic_claim"])
        self.assertEqual(result.training_report.reproduction_claim_status["status"], "no_claim")


if __name__ == "__main__":
    unittest.main()
