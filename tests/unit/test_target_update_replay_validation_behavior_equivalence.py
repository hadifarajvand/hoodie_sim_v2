from __future__ import annotations

from copy import deepcopy
import unittest

from src.analysis.target_update_replay_training_validation import TargetUpdateReplayValidationReport, build_target_update_replay_validation_report


class TargetUpdateReplayValidationBehaviorEquivalenceTests(unittest.TestCase):
    def test_repeated_validation_runs_match_on_summary_fields(self) -> None:
        first = build_target_update_replay_validation_report().to_dict()
        second = build_target_update_replay_validation_report().to_dict()
        for key in (
            "replay_summary",
            "optimizer_step_summary",
            "target_update_summary",
            "checkpoint_metadata_summary",
            "behavior_safety_summary",
            "remaining_blockers",
            "recommended_next_feature",
            "final_verdict",
        ):
            self.assertEqual(first[key], second[key], msg=key)

    def test_prerequisite_check_names_must_be_unique(self) -> None:
        payload = build_target_update_replay_validation_report().to_dict()
        duplicate = deepcopy(payload["prerequisite_tags_verified"])
        duplicate.append(deepcopy(duplicate[0]))
        payload["prerequisite_tags_verified"] = duplicate
        with self.assertRaises(ValueError):
            TargetUpdateReplayValidationReport(**payload)


if __name__ == "__main__":
    unittest.main()
