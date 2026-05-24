from __future__ import annotations

import unittest

from src.analysis.exposure_matrix_paper_mechanism_alignment import build_exposure_matrix_paper_mechanism_report


class ExposureMatrixPaperMechanismMetricsTests(unittest.TestCase):
    def test_exposure_metrics_are_trace_backed_and_complete(self) -> None:
        report = build_exposure_matrix_paper_mechanism_report()
        payload = report.to_dict()
        summary = payload["exposure_matrix_rerun_summary"]
        self.assertEqual(summary["decision_opportunity_count"], 1650)
        self.assertEqual(summary["selected_illegal_action_count"], 0)
        self.assertEqual(summary["selected_illegal_action_rate"], 0.0)
        self.assertTrue(summary["exposure_matrix_unblocked"])
        self.assertEqual(payload["legality_evidence_verified"]["legal_evidence_coverage_ratio"], 1.0)
        self.assertEqual(payload["selected_illegal_action_summary"]["selected_illegal_action_count"], 0)
        self.assertEqual(payload["selected_illegal_action_summary"]["selected_illegal_action_rate"], 0.0)

    def test_readiness_routing_matches_audits(self) -> None:
        report = build_exposure_matrix_paper_mechanism_report()
        payload = report.to_dict()
        decision = payload["training_readiness_decision"]
        self.assertEqual(decision["readiness_state"], "ready_for_feature_050")
        self.assertEqual(decision["final_verdict"], "paper_mechanism_alignment_ready_for_training_contract")
        self.assertEqual(decision["recommended_next_feature"], "Feature 050 — DDQN Training Contract Bundle")
        self.assertTrue(payload["observation_vector_audit"]["passed"])
        self.assertTrue(payload["paper_formula_unit_audit"]["passed"])


if __name__ == "__main__":
    unittest.main()
