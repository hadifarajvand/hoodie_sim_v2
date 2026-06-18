from __future__ import annotations

import unittest

from src.analysis.target_update_replay_training_validation import build_target_update_replay_validation_report


class TargetUpdateReplayValidationSchemaTests(unittest.TestCase):
    def test_top_level_schema(self) -> None:
        payload = build_target_update_replay_validation_report().to_dict()
        expected_keys = {
            "feature_id",
            "prerequisite_tags_verified",
            "feature_055_smoke_verified",
            "replay_insertion_validated",
            "replay_sampling_validated",
            "optimizer_step_counter_validated",
            "target_update_contract_validated",
            "target_sync_schedule_validated",
            "target_sync_before_threshold_blocked",
            "target_sync_at_threshold_validated",
            "checkpoint_metadata_validated",
            "replay_summary",
            "optimizer_step_summary",
            "target_update_summary",
            "checkpoint_metadata_summary",
            "behavior_safety_summary",
            "remaining_blockers",
            "recommended_next_feature",
            "final_verdict",
        }
        self.assertEqual(set(payload), expected_keys)
        self.assertEqual(payload["feature_id"], "056-target-update-and-replay-training-validation")
        self.assertTrue(payload["feature_055_smoke_verified"])
        self.assertTrue(payload["replay_insertion_validated"])
        self.assertTrue(payload["replay_sampling_validated"])
        self.assertTrue(payload["optimizer_step_counter_validated"])
        self.assertTrue(payload["target_update_contract_validated"])
        self.assertTrue(payload["target_sync_schedule_validated"])
        self.assertTrue(payload["target_sync_before_threshold_blocked"])
        self.assertTrue(payload["target_sync_at_threshold_validated"])
        self.assertTrue(payload["checkpoint_metadata_validated"])
        self.assertTrue(payload["replay_summary"]["replay_inserted"])
        self.assertGreater(payload["replay_summary"]["replay_size"], 0)
        self.assertGreater(payload["replay_summary"]["sampled_batch_size"], 0)
        self.assertTrue(all(payload["replay_summary"]["sampled_field_coverage"].values()))
        self.assertTrue(payload["optimizer_step_summary"]["optimizer_step_monotonic"])
        self.assertGreater(payload["optimizer_step_summary"]["optimizer_step_count"], 0)
        self.assertEqual(payload["optimizer_step_summary"]["optimizer_step_sequence"], list(range(1, payload["optimizer_step_summary"]["optimizer_step_count"] + 1)))
        self.assertTrue(payload["target_update_summary"]["no_sync_before_threshold"])
        self.assertTrue(payload["target_update_summary"]["sync_at_threshold"])
        self.assertEqual(payload["target_update_summary"]["target_update_unit"], "optimizer_step")
        self.assertEqual(payload["target_update_summary"]["target_update_frequency"], 2000)
        self.assertTrue(payload["checkpoint_metadata_summary"]["metadata_valid"])
        self.assertEqual(payload["final_verdict"], "target_update_replay_validation_passed")
        self.assertEqual(payload["recommended_next_feature"], "Feature 057 — Paper-Default Pilot Training Run")
        self.assertFalse(payload["remaining_blockers"])


if __name__ == "__main__":
    unittest.main()
