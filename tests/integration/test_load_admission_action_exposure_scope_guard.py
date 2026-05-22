from __future__ import annotations

import unittest

from src.analysis.load_admission_action_exposure_review.runner import run_load_admission_action_exposure_review


class LoadAdmissionActionExposureScopeGuardTest(unittest.TestCase):
    def test_scope_guards_true(self) -> None:
        payload = run_load_admission_action_exposure_review().to_dict()
        for key in (
            "no_runtime_repair_performed",
            "no_training_started",
            "no_optimizer_step",
            "no_replay_training",
            "no_target_update_execution",
            "no_dependency_drift",
            "no_environment_contract_drift",
            "no_policy_drift",
            "no_reward_timing_change",
            "no_timeout_contract_drift",
            "no_capacity_contract_drift",
            "no_transmission_contract_drift",
            "no_action_legality_drift",
            "no_curve_fitting",
            "no_simulator_output_tuning",
            "no_paper_reproduction_claim",
        ):
            self.assertTrue(payload[key])
        self.assertEqual(payload["final_verdict"], "diagnosis_inconclusive_requires_deeper_exposure_matrix")
        self.assertEqual(payload["recommended_next_feature"], "exposure-matrix review")
        self.assertEqual(payload["action_exposure_data_status"], "insufficient_data_for_legal_action_exposure")
        self.assertEqual(payload["legal_action_exposure_evidence_source"], "unavailable_in_committed_artifacts")
        self.assertFalse(payload["metric_population_consistency_verified"])
        self.assertTrue(payload["aggregate_metrics_not_sample_derived"])


if __name__ == "__main__":
    unittest.main()
