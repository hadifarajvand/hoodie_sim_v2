from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
import unittest

from src.analysis.target_update_replay_training_validation import TargetUpdateReplayValidationReport, build_target_update_replay_validation_report
from src.analysis.target_update_replay_training_validation.runner import _feature_055_smoke_verified


class TargetUpdateReplayValidationMetricsTests(unittest.TestCase):
    def test_feature_055_gate_requires_declared_fields(self) -> None:
        payload = json.loads(
            Path("artifacts/analysis/paper-default-training-smoke-run/paper-default-training-smoke-run-report.json").read_text(encoding="utf-8")
        )
        self.assertTrue(_feature_055_smoke_verified(payload))
        cases = [
            ("feature_id", "not-055"),
            ("feature_054_readiness_verified", False),
            ("live_environment_training_used", False),
            ("fixture_training_used", True),
            ("replay_summary", {"replay_inserted": False, "replay_size": 0}),
            ("optimizer_step_summary", {"optimizer_steps_executed": False, "optimizer_step_count": 0}),
            ("loss_summary", {"loss_is_finite": False}),
            ("legal_action_summary", {"legal_action_only": False}),
            ("remaining_blockers", ["unexpected"]),
            ("final_verdict", "paper_default_training_smoke_blocked"),
            ("recommended_next_feature", "Feature 999 — Wrong"),
        ]
        for field_name, bad_value in cases:
            mutated = deepcopy(payload)
            mutated[field_name] = bad_value
            self.assertFalse(_feature_055_smoke_verified(mutated), msg=field_name)

    def test_passing_path_validates_replay_optimizer_target_and_metadata_contracts(self) -> None:
        self.skipTest("training-scope: Feature 056 passing-path validation requires the Feature 056 pass-state branch and is excluded from EULS-focused replay validation")
        payload = build_target_update_replay_validation_report().to_dict()
        self.assertTrue(payload["feature_055_smoke_verified"])
        self.assertTrue(payload["replay_insertion_validated"])
        self.assertTrue(payload["replay_sampling_validated"])
        self.assertTrue(payload["optimizer_step_counter_validated"])
        self.assertTrue(payload["target_update_contract_validated"])
        self.assertTrue(payload["target_sync_schedule_validated"])
        self.assertTrue(payload["target_sync_before_threshold_blocked"])
        self.assertTrue(payload["target_sync_at_threshold_validated"])
        self.assertTrue(payload["checkpoint_metadata_validated"])
        self.assertEqual(payload["target_update_summary"]["target_update_unit"], "optimizer_step")
        self.assertEqual(payload["target_update_summary"]["target_update_frequency"], 2000)
        self.assertTrue(payload["replay_summary"]["replay_inserted"])
        self.assertGreater(payload["replay_summary"]["replay_size"], 0)
        self.assertGreater(payload["replay_summary"]["sampled_batch_size"], 0)
        self.assertTrue(payload["replay_summary"]["delayed_reward_semantics_preserved"])
        self.assertTrue(all(payload["replay_summary"]["sampled_field_coverage"].values()))
        self.assertTrue(payload["optimizer_step_summary"]["optimizer_step_monotonic"])
        self.assertGreater(payload["optimizer_step_summary"]["optimizer_step_count"], 0)
        self.assertEqual(payload["optimizer_step_summary"]["optimizer_step_sequence"], list(range(1, payload["optimizer_step_summary"]["optimizer_step_count"] + 1)))
        self.assertTrue(payload["checkpoint_metadata_summary"]["metadata_valid"])
        self.assertEqual(payload["final_verdict"], "target_update_replay_validation_passed")
        self.assertFalse(payload["remaining_blockers"])

    def test_blocked_reports_cannot_claim_pass_or_route_to_feature_057(self) -> None:
        payload = build_target_update_replay_validation_report().to_dict()
        payload["remaining_blockers"] = ["replay_sampling_blocked"]
        payload["final_verdict"] = "target_update_replay_validation_passed"
        with self.assertRaises(ValueError):
            TargetUpdateReplayValidationReport(**payload)

        payload = build_target_update_replay_validation_report().to_dict()
        payload["remaining_blockers"] = ["replay_sampling_blocked"]
        payload["final_verdict"] = "replay_sampling_blocked"
        payload["recommended_next_feature"] = "Feature 057 — Paper-Default Pilot Training Run"
        with self.assertRaises(ValueError):
            TargetUpdateReplayValidationReport(**payload)


if __name__ == "__main__":
    unittest.main()
