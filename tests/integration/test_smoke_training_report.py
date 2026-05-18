from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.smoke_training import SmokeTrainingConfig, run_smoke_training, write_smoke_training_report


class SmokeTrainingReportIntegrationTests(unittest.TestCase):
    def test_smoke_report_schema(self) -> None:
        report = run_smoke_training(SmokeTrainingConfig())
        payload = report.to_dict()
        required_keys = {
            "feature_id",
            "prerequisite_tags_verified",
            "smoke_scope",
            "dependency_status",
            "network_contract_verified",
            "replay_contract_verified",
            "delayed_reward_contract_verified",
            "seed_protocol_verified",
            "smoke_batch_summary",
            "optimizer_step_summary",
            "loss_summary",
            "parameter_update_summary",
            "deterministic_repeatability_verified",
            "target_update_blocked_reason",
            "feature_038_training_readiness_block_respected",
            "no_paper_reproduction_claim",
            "no_curve_fitting",
            "no_full_training",
            "no_campaign_execution",
            "no_baseline_comparison",
            "no_target_update_execution",
            "no_dependency_drift",
            "no_environment_contract_drift",
            "no_policy_drift",
            "no_reward_timing_change",
            "final_verdict",
        }
        self.assertTrue(required_keys.issubset(payload))
        self.assertEqual(payload["feature_id"], "040-smoke-training")
        self.assertEqual(payload["dependency_status"], "available_existing_torch")
        self.assertEqual(payload["final_verdict"], "smoke_training_passed")
        self.assertTrue(payload["feature_038_training_readiness_block_respected"])
        self.assertTrue(payload["no_paper_reproduction_claim"])
        self.assertTrue(payload["no_curve_fitting"])
        self.assertTrue(payload["no_full_training"])
        self.assertTrue(payload["no_campaign_execution"])
        self.assertTrue(payload["no_baseline_comparison"])
        self.assertTrue(payload["no_target_update_execution"])
        self.assertTrue(payload["no_dependency_drift"])
        self.assertTrue(payload["no_environment_contract_drift"])
        self.assertTrue(payload["no_policy_drift"])
        self.assertTrue(payload["no_reward_timing_change"])
        self.assertEqual(payload["smoke_scope"]["smoke_only"], True)
        self.assertEqual(payload["smoke_scope"]["full_training"], False)
        self.assertEqual(payload["smoke_scope"]["target_update_executed"], False)
        self.assertEqual(payload["network_contract_verified"]["action_count"], 3)
        self.assertEqual(payload["network_contract_verified"]["lookback_w"], 10)
        self.assertEqual(payload["network_contract_verified"]["state_dim"], 3)
        self.assertTrue(payload["replay_contract_verified"]["non_terminal_reward_available_false"])
        self.assertTrue(payload["replay_contract_verified"]["terminal_reward_available_true"])
        self.assertTrue(payload["replay_contract_verified"]["pending_at_horizon_preserved"])
        self.assertTrue(payload["delayed_reward_contract_verified"]["pending_at_horizon_is_non_terminal"])
        self.assertEqual(payload["seed_protocol_verified"]["model_initialization_seed"], 19)

    def test_smoke_report_artifacts_are_written(self) -> None:
        report = run_smoke_training(SmokeTrainingConfig())
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "artifacts/analysis/smoke-training"
            json_path, md_path = write_smoke_training_report(report, output_dir)
            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["feature_id"], "040-smoke-training")
            self.assertEqual(payload["dependency_status"], "available_existing_torch")
            self.assertEqual(payload["final_verdict"], "smoke_training_passed")
            markdown = md_path.read_text(encoding="utf-8")
            self.assertIn("smoke_training_passed", markdown)
            self.assertIn("no_paper_reproduction_claim", markdown)
            self.assertIn("target_update_blocked_reason", markdown)


if __name__ == "__main__":
    unittest.main()
