from __future__ import annotations

import unittest

from src.analysis.legality_evidence_expansion import build_legality_evidence_report


class LegalityEvidenceExpansionIntegrationTests(unittest.TestCase):
    def test_report_routes_to_feature_049_only_when_coverage_sufficient(self) -> None:
        report = build_legality_evidence_report()
        payload = report.to_dict()
        if payload["legal_evidence_coverage_ratio"] in (0.0, None):
            self.assertEqual(payload["recommended_next_feature"], "public legality helper feature before exposure-matrix rerun")
            self.assertFalse(payload["exposure_matrix_unblocked"])
        else:
            self.assertEqual(payload["recommended_next_feature"], "Feature 049 - Exposure-Matrix Rerun with Legality Evidence")
            self.assertTrue(payload["exposure_matrix_unblocked"])

    def test_final_verdict_matches_coverage_ratio(self) -> None:
        report = build_legality_evidence_report()
        payload = report.to_dict()
        if payload["legal_evidence_coverage_ratio"] in (0.0, None):
            self.assertEqual(payload["final_verdict"], "legality_evidence_unavailable_requires_runtime_public_helper")
        else:
            self.assertEqual(payload["final_verdict"], "legality_evidence_ready_for_exposure_matrix_rerun")

    def test_no_runtime_training_policy_dependency_drift(self) -> None:
        report = build_legality_evidence_report()
        payload = report.to_dict()
        for flag in (
            "no_runtime_repair_performed",
            "no_training_started",
            "no_optimizer_step",
            "no_replay_training",
            "no_target_update_execution",
            "no_dependency_drift",
            "no_policy_drift",
            "no_reward_timing_change",
            "no_timeout_contract_drift",
            "no_capacity_contract_drift",
            "no_transmission_contract_drift",
            "no_action_legality_drift",
            "no_action_selection_drift",
            "no_curve_fitting",
            "no_simulator_output_tuning",
            "no_paper_reproduction_claim",
        ):
            self.assertTrue(payload[flag])


if __name__ == "__main__":
    unittest.main()
