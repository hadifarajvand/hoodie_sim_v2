from __future__ import annotations

import unittest

from src.analysis.exposure_matrix_paper_mechanism_rerun_with_outcome_evidence import (
    ALLOWED_ALIGNMENT_STATUSES,
    ALLOWED_FINAL_VERDICTS,
    build_exposure_matrix_paper_mechanism_rerun_report,
)


class ExposureMatrixPaperMechanismRerunSchemaTests(unittest.TestCase):
    def test_top_level_contract(self) -> None:
        payload = build_exposure_matrix_paper_mechanism_rerun_report().to_dict()
        required_keys = {
            "feature_id",
            "prerequisite_tags_verified",
            "prior_feature_gates_verified",
            "feature_052_trace_readiness_verified",
            "feature_052_readiness_verified",
            "observation_vector_alignment_status",
            "formula_unit_alignment_status",
            "exposure_matrix_alignment_status",
            "selected_action_outcome_alignment_status",
            "training_readiness_contract_status",
            "paper_mechanism_alignment_ready",
            "remaining_blockers",
            "recommended_next_feature",
            "behavior_equivalence_summary",
            "behavior_equivalence_passed",
            "no_runtime_repair_performed",
            "no_training_started",
            "no_optimizer_step",
            "no_replay_training",
            "no_target_update_execution",
            "no_checkpoint_written",
            "no_campaign_run",
            "no_dependency_drift",
            "no_policy_drift",
            "no_environment_drift",
            "no_prior_artifact_rewrite",
            "no_paper_reproduction_claim",
            "final_verdict",
        }
        self.assertTrue(required_keys.issubset(payload.keys()))
        self.assertIn("no_checkpoint_generation", payload)
        self.assertIn("no_full_campaign", payload)
        self.assertIn("no_dependency_changes", payload)
        self.assertIn("no_runtime_semantic_changes", payload)

    def test_alignment_status_vocab(self) -> None:
        payload = build_exposure_matrix_paper_mechanism_rerun_report().to_dict()
        for key in (
            "observation_vector_alignment_status",
            "formula_unit_alignment_status",
            "exposure_matrix_alignment_status",
            "selected_action_outcome_alignment_status",
            "training_readiness_contract_status",
        ):
            self.assertIn(payload[key], ALLOWED_ALIGNMENT_STATUSES)

    def test_behavior_equivalence_contract(self) -> None:
        payload = build_exposure_matrix_paper_mechanism_rerun_report().to_dict()
        names = [check["name"] for check in payload["behavior_equivalence_summary"]["checks"]]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(payload["behavior_equivalence_passed"], payload["behavior_equivalence_summary"]["passed"])

    def test_final_verdict_vocab(self) -> None:
        payload = build_exposure_matrix_paper_mechanism_rerun_report().to_dict()
        self.assertIn(payload["final_verdict"], ALLOWED_FINAL_VERDICTS)


if __name__ == "__main__":
    unittest.main()
