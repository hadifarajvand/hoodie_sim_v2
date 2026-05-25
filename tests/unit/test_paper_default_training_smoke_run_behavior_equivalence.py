from __future__ import annotations

from copy import deepcopy
import unittest

from src.analysis.paper_default_training_smoke_run import PaperDefaultTrainingSmokeReport, run_paper_default_training_smoke


class PaperDefaultTrainingSmokeRunBehaviorEquivalenceTests(unittest.TestCase):
    def test_repeated_smoke_runs_match_on_the_recorded_summary_fields(self) -> None:
        first = run_paper_default_training_smoke().to_dict()
        second = run_paper_default_training_smoke().to_dict()
        for key in (
            "paper_default_smoke_scope",
            "replay_summary",
            "optimizer_step_summary",
            "loss_summary",
            "checkpoint_summary",
            "legal_action_summary",
            "delayed_reward_contract_verified",
            "train_eval_contract_verified",
            "behavior_safety_summary",
            "remaining_blockers",
            "recommended_next_feature",
            "final_verdict",
        ):
            self.assertEqual(first[key], second[key], msg=key)

    def test_prerequisite_named_checks_must_be_unique(self) -> None:
        payload = run_paper_default_training_smoke().to_dict()
        duplicate = deepcopy(payload["prerequisite_tags_verified"])
        duplicate.append(deepcopy(duplicate[0]))
        payload["prerequisite_tags_verified"] = duplicate
        with self.assertRaises(ValueError):
            PaperDefaultTrainingSmokeReport(**payload)


if __name__ == "__main__":
    unittest.main()
