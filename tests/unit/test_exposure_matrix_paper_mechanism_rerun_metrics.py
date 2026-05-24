from __future__ import annotations

import unittest

from src.analysis.exposure_matrix_paper_mechanism_rerun_with_outcome_evidence import build_exposure_matrix_paper_mechanism_rerun_report


class ExposureMatrixPaperMechanismRerunMetricsTests(unittest.TestCase):
    def test_feature_052_gate_and_alignment_statuses(self) -> None:
        payload = build_exposure_matrix_paper_mechanism_rerun_report().to_dict()
        self.assertTrue(payload["feature_052_trace_readiness_verified"])
        self.assertTrue(payload["feature_052_readiness_verified"])
        self.assertEqual(payload["observation_vector_alignment_status"], "available")
        self.assertEqual(payload["formula_unit_alignment_status"], "available")
        self.assertEqual(payload["exposure_matrix_alignment_status"], "available")
        self.assertEqual(payload["selected_action_outcome_alignment_status"], "available")
        self.assertEqual(payload["training_readiness_contract_status"], "available")
        self.assertTrue(payload["paper_mechanism_alignment_ready"])
        self.assertEqual(payload["remaining_blockers"], [])
        self.assertEqual(payload["recommended_next_feature"], "Feature 054 — Training Readiness Contract")
        self.assertEqual(payload["final_verdict"], "paper_mechanism_alignment_ready_for_training_contract")

    def test_drift_and_hygiene_flags_remain_true(self) -> None:
        payload = build_exposure_matrix_paper_mechanism_rerun_report().to_dict()
        for flag in (
            "no_runtime_repair_performed",
            "no_training_started",
            "no_optimizer_step",
            "no_replay_training",
            "no_target_update_execution",
            "no_checkpoint_written",
            "no_checkpoint_generation",
            "no_campaign_run",
            "no_full_campaign",
            "no_dependency_drift",
            "no_dependency_changes",
            "no_policy_drift",
            "no_environment_drift",
            "no_runtime_semantic_changes",
            "no_prior_artifact_rewrite",
            "no_paper_reproduction_claim",
        ):
            self.assertTrue(payload[flag])


if __name__ == "__main__":
    unittest.main()
