from __future__ import annotations

import unittest

from src.analysis.exposure_matrix_paper_mechanism_alignment import build_exposure_matrix_paper_mechanism_report


class ExposureMatrixPaperMechanismAlignmentIntegrationTests(unittest.TestCase):
    def test_report_routes_to_feature_050_when_audits_pass(self) -> None:
        report = build_exposure_matrix_paper_mechanism_report()
        payload = report.to_dict()
        self.assertEqual(report.final_verdict, "paper_mechanism_alignment_ready_for_training_contract")
        self.assertEqual(report.recommended_next_feature, "Feature 050 — DDQN Training Contract Bundle")
        self.assertEqual(payload["legality_evidence_verified"]["source_feature"], "048-legality-evidence-expansion")
        self.assertTrue(payload["legality_evidence_verified"]["exposure_matrix_unblocked"])
        self.assertEqual(payload["legal_vs_selected_action_matrix"]["matrix_complete"], True)
        self.assertTrue(payload["legal_vs_selected_action_matrix"]["trace_backed"])

    def test_prior_feature_gates_include_043_through_048(self) -> None:
        report = build_exposure_matrix_paper_mechanism_report()
        features = [entry["feature"] for entry in report.prior_feature_gates_verified if entry.get("verified") is True]
        self.assertEqual(features, ["037", "038", "039", "040", "041", "042", "043", "044", "045", "046", "047", "048"])


if __name__ == "__main__":
    unittest.main()
