from __future__ import annotations

import unittest

from src.analysis.training_readiness_contract import build_training_readiness_contract_report


class TrainingReadinessContractSchemaTests(unittest.TestCase):
    def test_top_level_contract(self) -> None:
        payload = build_training_readiness_contract_report().to_dict()
        expected_keys = {
            "feature_id",
            "prerequisite_tags_verified",
            "prior_feature_gates_verified",
            "feature_053_readiness_verified",
            "evidence_chain_ready_for_training_contract",
            "paper_default_config_locked",
            "observation_contract_locked",
            "action_contract_locked",
            "legality_contract_locked",
            "reward_contract_locked",
            "timeout_contract_locked",
            "capacity_contract_locked",
            "transmission_contract_locked",
            "queue_contract_locked",
            "metric_contract_locked",
            "seed_contract_locked",
            "artifact_contract_locked",
            "behavior_equivalence_summary",
            "behavior_equivalence_passed",
            "training_execution_allowed_next",
            "remaining_blockers",
            "recommended_next_feature",
            "no_training_started",
            "no_optimizer_step",
            "no_replay_training",
            "no_target_update_execution",
            "no_checkpoint_written",
            "no_campaign_run",
            "no_policy_drift",
            "no_runtime_semantic_changes",
            "no_dependency_drift",
            "no_prior_artifact_rewrite",
            "no_paper_reproduction_claim",
            "final_verdict",
        }
        self.assertEqual(set(payload.keys()), expected_keys)
        self.assertEqual(payload["feature_id"], "054-training-readiness-contract")
        self.assertEqual(payload["behavior_equivalence_passed"], payload["behavior_equivalence_summary"]["passed"])
        self.assertEqual(payload["recommended_next_feature"], "prerequisite evidence repair before training")


if __name__ == "__main__":
    unittest.main()
