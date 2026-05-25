from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.full_paper_default_training_campaign_gate import build_full_paper_default_training_campaign_gate_report
from src.analysis.full_paper_default_training_campaign_gate.config import FullPaperDefaultTrainingCampaignGateConfig


class FullPaperDefaultTrainingCampaignGateIntegrationTests(unittest.TestCase):
    def test_generated_report_reaches_ready_verdict(self) -> None:
        payload = build_full_paper_default_training_campaign_gate_report().to_dict()
        self.assertTrue(payload["feature_058_harness_verified"])
        self.assertEqual(payload["remaining_blockers"], [])
        self.assertEqual(payload["final_verdict"], "full_paper_default_training_campaign_gate_ready")
        self.assertEqual(payload["recommended_next_feature"], "Feature 060 — Full Paper-Default Training Campaign Execution")

    def test_feature_058_readiness_gate_blocks_bad_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_report = Path(tmp) / "bad-058.json"
            bad_report.write_text(
                json.dumps(
                    {
                        "feature_id": "058-evaluation-trace-bank-baseline-harness",
                        "feature_057_pilot_verified": True,
                        "evaluation_trace_bank_summary": {"evaluation_trace_count": 0, "bank_generation_repeatable": False},
                        "train_eval_separation_summary": {"train_eval_trace_banks_disjoint": True, "evaluation_on_training_traces": False},
                        "baseline_policy_registry_summary": {"baseline_policy_count": 1, "action_contract_compatible": True},
                        "baseline_evaluation_harness_summary": {"evaluated_policy_count": 1},
                        "metric_schema_summary": {"metric_schema_complete": True},
                        "determinism_summary": {"repeatability_proven": True},
                        "behavior_safety_summary": {
                            "no_training_execution": True,
                            "no_optimizer_execution": True,
                            "no_replay_mutation": True,
                            "no_checkpoint_binary_written": True,
                            "no_full_campaign": True,
                            "no_paper_reproduction_claim": True,
                            "no_performance_claim": True,
                        },
                        "remaining_blockers": ["evaluation_trace_bank_blocked"],
                        "final_verdict": "evaluation_trace_bank_blocked",
                        "recommended_next_feature": "Repair Feature 058",
                    }
                ),
                encoding="utf-8",
            )
            config = FullPaperDefaultTrainingCampaignGateConfig(feature_058_report_path=bad_report)
            payload = build_full_paper_default_training_campaign_gate_report(config).to_dict()
        self.assertFalse(payload["feature_058_harness_verified"])
        self.assertEqual(payload["final_verdict"], "feature_058_prerequisite_blocked")
        self.assertIn("feature_058_report_valid", payload["remaining_blockers"])
        self.assertNotEqual(payload["recommended_next_feature"], "Feature 060 — Full Paper-Default Training Campaign Execution")

    def test_gate_does_not_execute_campaign_training_or_optimizer(self) -> None:
        payload = build_full_paper_default_training_campaign_gate_report().to_dict()
        self.assertFalse(payload["campaign_scope_summary"]["full_campaign_executed_this_feature"])
        self.assertFalse(payload["training_execution_gate_summary"]["training_executed_this_feature"])
        self.assertFalse(payload["training_execution_gate_summary"]["optimizer_executed_this_feature"])
        self.assertFalse(payload["training_execution_gate_summary"]["replay_mutated_this_feature"])
        self.assertFalse(payload["training_execution_gate_summary"]["checkpoint_binary_written_this_feature"])

    def test_evaluation_harness_gate_carries_feature_058_readiness(self) -> None:
        payload = build_full_paper_default_training_campaign_gate_report().to_dict()
        gate = payload["evaluation_harness_gate_summary"]
        self.assertTrue(gate["evaluation_trace_bank_ready"])
        self.assertTrue(gate["train_eval_trace_banks_disjoint"])
        self.assertTrue(gate["baseline_policy_registry_ready"])
        self.assertTrue(gate["baseline_harness_ready"])
        self.assertTrue(gate["metric_schema_complete"])
        self.assertTrue(gate["determinism_ready"])


if __name__ == "__main__":
    unittest.main()
