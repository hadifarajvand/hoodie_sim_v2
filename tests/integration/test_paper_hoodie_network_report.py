from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.paper_hoodie_network_implementation import build_network_implementation_report, write_network_implementation_report


class PaperHoodieNetworkReportIntegrationTests(unittest.TestCase):
    def test_network_implementation_report_schema(self) -> None:
        report = build_network_implementation_report()
        payload = report.to_dict()
        required_keys = {
            "feature_id",
            "prerequisite_tags_verified",
            "dependency_status",
            "architecture_config",
            "q_network_hidden_layers_verified",
            "lstm_hidden_layers_verified",
            "q_lstm_config_separation_verified",
            "dueling_head_verified",
            "double_dqn_api_verified",
            "online_target_network_compatibility_verified",
            "state_action_contract_refs",
            "shape_validation_summary",
            "deterministic_initialization_verified",
            "feature_038_training_readiness_block_respected",
            "no_training_started",
            "no_optimizer_step",
            "no_replay_execution",
            "no_target_update_execution",
            "no_environment_contract_drift",
            "no_reward_timing_change",
            "no_policy_drift",
            "no_dependency_drift",
            "no_curve_fitting",
            "no_paper_reproduction_claim",
            "final_verdict",
        }
        self.assertTrue(required_keys.issubset(payload))
        self.assertEqual(payload["feature_id"], "039-paper-hoodie-network-implementation")
        self.assertEqual(payload["dependency_status"], "blocked_missing_existing_torch")
        self.assertEqual(payload["final_verdict"], "dependency_blocked")
        self.assertTrue(payload["q_network_hidden_layers_verified"])
        self.assertTrue(payload["lstm_hidden_layers_verified"])
        self.assertTrue(payload["q_lstm_config_separation_verified"])
        self.assertFalse(payload["dueling_head_verified"])
        self.assertFalse(payload["double_dqn_api_verified"])
        self.assertFalse(payload["online_target_network_compatibility_verified"])
        self.assertTrue(payload["feature_038_training_readiness_block_respected"])
        self.assertTrue(payload["no_training_started"])
        self.assertTrue(payload["no_optimizer_step"])
        self.assertTrue(payload["no_replay_execution"])
        self.assertTrue(payload["no_target_update_execution"])
        self.assertTrue(payload["no_environment_contract_drift"])
        self.assertTrue(payload["no_reward_timing_change"])
        self.assertTrue(payload["no_policy_drift"])
        self.assertTrue(payload["no_dependency_drift"])
        self.assertTrue(payload["no_curve_fitting"])
        self.assertTrue(payload["no_paper_reproduction_claim"])

    def test_report_writes_json_and_markdown(self) -> None:
        report = build_network_implementation_report()
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path, md_path = write_network_implementation_report(report, Path(tmpdir) / "artifacts/analysis/paper-hoodie-network-implementation")
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())
            self.assertEqual(payload["feature_id"], "039-paper-hoodie-network-implementation")
            self.assertEqual(payload["dependency_status"], "blocked_missing_existing_torch")
            self.assertEqual(payload["final_verdict"], "dependency_blocked")
            self.assertIn("dependency_status", md_path.read_text(encoding="utf-8"))
            self.assertIn("no_paper_reproduction_claim", md_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
