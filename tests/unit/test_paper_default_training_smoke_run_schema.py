from __future__ import annotations

import unittest

from src.analysis.paper_default_training_smoke_run import build_paper_default_training_smoke_report


class PaperDefaultTrainingSmokeRunSchemaTests(unittest.TestCase):
    def test_top_level_schema(self) -> None:
        payload = build_paper_default_training_smoke_report().to_dict()
        expected_keys = {
            "feature_id",
            "prerequisite_tags_verified",
            "feature_054_readiness_verified",
            "paper_default_smoke_scope",
            "live_environment_training_used",
            "fixture_training_used",
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
        }
        self.assertEqual(set(payload), expected_keys)
        self.assertEqual(payload["feature_id"], "055-paper-default-training-smoke-run")
        self.assertTrue(payload["feature_054_readiness_verified"])
        self.assertTrue(payload["live_environment_training_used"])
        self.assertFalse(payload["fixture_training_used"])
        self.assertEqual(payload["recommended_next_feature"], "Feature 056 — Target Update and Replay Training Validation")
        self.assertEqual(payload["final_verdict"], "paper_default_training_smoke_passed")
        self.assertFalse(payload["remaining_blockers"])


if __name__ == "__main__":
    unittest.main()
