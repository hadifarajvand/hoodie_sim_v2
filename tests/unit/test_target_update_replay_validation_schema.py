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
        self.assertEqual(payload["recommended_next_feature"], "Feature 057 — Paper-Default Pilot Training Run")


if __name__ == "__main__":
    unittest.main()
