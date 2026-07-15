from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src.analysis.evaluation_trace_bank_baseline_harness import (
    build_evaluation_trace_bank_baseline_harness_report,
    build_evaluation_trace_bank_summary,
)
from src.analysis.evaluation_trace_bank_baseline_harness.config import EvaluationTraceBankBaselineHarnessConfig


class EvaluationTraceBankBaselineHarnessIntegrationTests(unittest.TestCase):
    def test_generated_report_reaches_ready_verdict(self) -> None:
        import src.analysis.evaluation_trace_bank_baseline_harness.runner as runner
        config = EvaluationTraceBankBaselineHarnessConfig(feature_057_report_path=Path("/tmp/feature-057.json"))
        ready_prereqs = [
            {"name": "branch", "verified": True},
            {"name": "not_main", "verified": True},
            {"name": "base_contains_feature_057_complete", "verified": True},
            {"name": "base_is_branch_base", "verified": True},
            {"name": "feature_057_report_valid", "verified": True},
            {"name": "feature_056_report_valid", "verified": True},
            {"name": "feature_055_report_valid", "verified": True},
            {"name": "status_paths_approved", "verified": True},
            {"name": "staged_paths_approved", "verified": True},
            {"name": "committed_paths_approved", "verified": True},
        ]
        with mock.patch.object(runner, "_status_paths", return_value=[]):
            with mock.patch.object(runner, "_staged_paths", return_value=[]):
                with mock.patch.object(runner, "_diff_names", return_value=[]):
                    with mock.patch.object(runner, "_build_prerequisite_tags_verified", return_value=ready_prereqs):
                        with mock.patch.object(runner, "_feature_057_pilot_verified", return_value=True):
                            with mock.patch.object(runner, "_load_json", return_value={"feature_id": "057-paper-default-pilot-training-run"}):
                                with mock.patch.object(runner, "build_evaluation_trace_bank_summary", return_value={"evaluation_trace_bank_id": "eval-bank", "evaluation_trace_count": 1, "seed_bundle": {"seed": 1}, "trace_identities": ["a"], "repeatability_evidence": ["sig"], "bank_generation_repeatable": True, "trace_bank_signature": "sig", "trace_hashes": ["a"], "trace_ids": ["a"]}):
                                    with mock.patch.object(runner, "_build_train_eval_separation_summary", return_value={"training_trace_bank_id": "train-bank", "evaluation_trace_bank_id": "eval-bank", "training_trace_bank_exists": True, "evaluation_trace_bank_exists": True, "training_trace_ids": ["t1"], "evaluation_trace_ids": ["e1"], "overlap_trace_ids": [], "train_eval_trace_banks_disjoint": True, "evaluation_on_training_traces": False}):
                                        with mock.patch.object(runner, "build_baseline_policy_registry", return_value={"baseline_policy_count": 1, "action_contract_compatible": True}):
                                            with mock.patch.object(runner, "_evaluate_baselines", return_value={"evaluated_policy_count": 1}):
                                                with mock.patch.object(runner, "_build_metric_schema_summary", return_value={"metric_schema_complete": True}):
                                                    with mock.patch.object(runner, "_build_behavior_safety_summary", return_value={"no_policy_drift": True, "no_environment_contract_drift": True}):
                                                        payload = build_evaluation_trace_bank_baseline_harness_report(config).to_dict()
        self.assertTrue(payload["feature_057_pilot_verified"])
        self.assertEqual(payload["remaining_blockers"], [])
        self.assertEqual(payload["final_verdict"], "evaluation_trace_bank_baseline_harness_ready")
        self.assertEqual(payload["recommended_next_feature"], "Feature 059 — Full Paper-Default Training Campaign Gate")

    def test_evaluation_trace_bank_is_deterministic_and_non_empty(self) -> None:
        first = build_evaluation_trace_bank_summary()
        second = build_evaluation_trace_bank_summary()
        self.assertGreater(first["evaluation_trace_count"], 0)
        self.assertEqual(first["trace_bank_signature"], second["trace_bank_signature"])
        self.assertEqual(first["trace_hashes"], second["trace_hashes"])
        self.assertTrue(first["bank_generation_repeatable"])

    def test_train_eval_trace_banks_are_disjoint(self) -> None:
        import src.analysis.evaluation_trace_bank_baseline_harness.runner as runner
        with mock.patch.object(runner, "_status_paths", return_value=[]):
            with mock.patch.object(runner, "_staged_paths", return_value=[]):
                with mock.patch.object(runner, "_diff_names", return_value=[]):
                    with mock.patch.object(runner, "_build_prerequisite_tags_verified", return_value=[{"name": "branch", "verified": True}]):
                        with mock.patch.object(runner, "_feature_057_pilot_verified", return_value=True):
                            with mock.patch.object(runner, "_build_train_eval_separation_summary", return_value={"training_trace_bank_id": "train-bank", "evaluation_trace_bank_id": "eval-bank", "training_trace_bank_exists": True, "evaluation_trace_bank_exists": True, "training_trace_ids": ["t1"], "evaluation_trace_ids": ["e1"], "overlap_trace_ids": [], "train_eval_trace_banks_disjoint": True, "evaluation_on_training_traces": False}):
                                with mock.patch.object(runner, "build_evaluation_trace_bank_summary", return_value={"evaluation_trace_bank_id": "eval-bank", "evaluation_trace_count": 1, "seed_bundle": {"seed": 1}, "trace_identities": ["a"], "repeatability_evidence": ["sig"], "bank_generation_repeatable": True, "trace_bank_signature": "sig", "trace_hashes": ["a"], "trace_ids": ["a"]}):
                                    with mock.patch.object(runner, "build_baseline_policy_registry", return_value={"baseline_policy_count": 1, "action_contract_compatible": True}):
                                        with mock.patch.object(runner, "_evaluate_baselines", return_value={"evaluated_policy_count": 1}):
                                            with mock.patch.object(runner, "_build_metric_schema_summary", return_value={"metric_schema_complete": True}):
                                                with mock.patch.object(runner, "_build_behavior_safety_summary", return_value={"no_policy_drift": True, "no_environment_contract_drift": True}):
                                                    payload = build_evaluation_trace_bank_baseline_harness_report().to_dict()
        separation = payload["train_eval_separation_summary"]
        self.assertTrue(separation["training_trace_bank_exists"])
        self.assertTrue(separation["evaluation_trace_bank_exists"])
        self.assertEqual(separation["overlap_trace_ids"], [])
        self.assertTrue(separation["train_eval_trace_banks_disjoint"])
        self.assertFalse(separation["evaluation_on_training_traces"])

    def test_feature_057_readiness_gate_blocks_bad_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_report = Path(tmp) / "bad-057.json"
            bad_report.write_text(
                json.dumps(
                    {
                        "feature_id": "057-paper-default-pilot-training-run",
                        "feature_056_validation_verified": True,
                        "live_environment_training_used": True,
                        "fixture_training_used": False,
                        "replay_summary": {"replay_growth_validated": False},
                        "optimizer_summary": {"optimizer_progress_validated": True},
                        "loss_summary": {"all_losses_finite": True},
                        "legal_action_summary": {"legal_action_only": True},
                        "checkpoint_summary": {"checkpoint_schema_valid": True},
                        "train_eval_contract_verified": {"train_eval_trace_banks_disjoint": True},
                        "remaining_blockers": ["replay_growth_not_validated"],
                        "final_verdict": "replay_growth_blocked",
                        "recommended_next_feature": "Repair Feature 057",
                    }
                ),
                encoding="utf-8",
            )
            config = EvaluationTraceBankBaselineHarnessConfig(feature_057_report_path=bad_report)
            payload = build_evaluation_trace_bank_baseline_harness_report(config).to_dict()
        self.assertFalse(payload["feature_057_pilot_verified"])
        self.assertEqual(payload["final_verdict"], "feature_057_prerequisite_blocked")
        self.assertIn("feature_057_report_valid", payload["remaining_blockers"])
        self.assertNotEqual(payload["recommended_next_feature"], "Feature 059 — Full Paper-Default Training Campaign Gate")


if __name__ == "__main__":
    unittest.main()
