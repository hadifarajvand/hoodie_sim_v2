from __future__ import annotations

import json
import unittest

from src.analysis.paper_default_pilot_training_run.runner import generate_paper_default_pilot_training_run_artifacts


class PaperDefaultPilotTrainingRunReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report, cls.json_path, cls.md_path = generate_paper_default_pilot_training_run_artifacts()
        cls.payload = json.loads(cls.json_path.read_text(encoding="utf-8"))

    def test_required_top_level_fields_exist(self) -> None:
        expected_fields = {
            "feature_id",
            "prerequisite_tags_verified",
            "feature_056_validation_verified",
            "pilot_scope",
            "live_environment_training_used",
            "fixture_training_used",
            "episode_summary",
            "replay_summary",
            "optimizer_summary",
            "target_update_summary",
            "loss_summary",
            "reward_summary",
            "legal_action_summary",
            "checkpoint_summary",
            "train_eval_contract_verified",
            "behavior_safety_summary",
            "remaining_blockers",
            "recommended_next_feature",
            "final_verdict",
        }
        self.assertTrue(expected_fields.issubset(self.payload))

    def test_report_matches_expected_passing_contract(self) -> None:
        self.assertEqual(self.payload["feature_id"], "057-paper-default-pilot-training-run")
        self.assertTrue(self.payload["feature_056_validation_verified"])
        self.assertTrue(self.payload["live_environment_training_used"])
        self.assertFalse(self.payload["fixture_training_used"])
        self.assertEqual(self.payload["final_verdict"], "paper_default_pilot_training_passed")
        self.assertEqual(self.payload["recommended_next_feature"], "Feature 058 — Evaluation Trace Bank and Baseline Evaluation Harness")
        self.assertEqual(self.payload["remaining_blockers"], [])

    def test_report_contains_growth_and_checkpoint_evidence(self) -> None:
        self.assertGreater(self.payload["replay_summary"]["replay_size"], self.payload["replay_summary"]["feature_055_smoke_replay_size"])
        self.assertGreater(self.payload["optimizer_summary"]["optimizer_step_count"], self.payload["optimizer_summary"]["feature_055_smoke_optimizer_step_count"])
        self.assertTrue(self.payload["checkpoint_summary"]["checkpoint_schema_valid"])
        self.assertTrue(self.payload["train_eval_contract_verified"]["train_eval_trace_banks_disjoint"])
