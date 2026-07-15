from __future__ import annotations

import unittest
from pathlib import Path

from src.analysis.paper_default_pilot_training_run.runner import generate_paper_default_pilot_training_run_artifacts


class PaperDefaultPilotTrainingRunIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report, cls.json_path, cls.md_path = generate_paper_default_pilot_training_run_artifacts()

    def test_report_artifacts_exist(self) -> None:
        self.assertTrue(self.json_path.exists())
        self.assertTrue(self.md_path.exists())

    def test_report_verdict_is_passing(self) -> None:
        payload = self.report.to_dict()
        self.assertEqual(payload["final_verdict"], "paper_default_pilot_training_passed")
        self.assertEqual(payload["recommended_next_feature"], "Feature 058 — Evaluation Trace Bank and Baseline Evaluation Harness")
        self.assertEqual(payload["remaining_blockers"], [])
        self.assertTrue(payload["feature_056_validation_verified"])
        self.assertTrue(payload["live_environment_training_used"])
        self.assertFalse(payload["fixture_training_used"])
        self.assertGreater(payload["pilot_scope"]["pilot_episodes"], 1)
        self.assertFalse(payload["pilot_scope"]["full_campaign"])
        self.assertFalse(payload["pilot_scope"]["baseline_comparison"])
        self.assertFalse(payload["pilot_scope"]["paper_reproduction_claim"])

    def test_growth_and_safety_evidence_is_positive(self) -> None:
        payload = self.report.to_dict()
        self.assertGreater(payload["replay_summary"]["replay_size"], payload["replay_summary"]["feature_055_smoke_replay_size"])
        self.assertGreater(payload["optimizer_summary"]["optimizer_step_count"], payload["optimizer_summary"]["feature_055_smoke_optimizer_step_count"])
        self.assertTrue(payload["replay_summary"]["replay_growth_validated"])
        self.assertTrue(payload["optimizer_summary"]["optimizer_progress_validated"])
        self.assertTrue(payload["loss_summary"]["all_losses_finite"])
        self.assertTrue(payload["reward_summary"]["delayed_reward_contract_preserved"])
        self.assertTrue(payload["legal_action_summary"]["legal_action_only"])
        self.assertTrue(payload["checkpoint_summary"]["checkpoint_schema_valid"])
        self.assertTrue(payload["train_eval_contract_verified"]["train_eval_trace_banks_disjoint"])
