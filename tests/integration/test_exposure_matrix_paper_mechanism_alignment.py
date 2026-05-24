from __future__ import annotations

import unittest

from src.analysis.exposure_matrix_paper_mechanism_alignment import build_exposure_matrix_paper_mechanism_report


class ExposureMatrixPaperMechanismAlignmentIntegrationTests(unittest.TestCase):
    def test_feature_050_not_recommended_from_placeholder_exposure_matrix(self) -> None:
        report = build_exposure_matrix_paper_mechanism_report()
        payload = report.to_dict()
        self.assertEqual(report.final_verdict, "insufficient_legality_or_trace_evidence")
        self.assertEqual(report.recommended_next_feature, "selected-action family evidence expansion before training")
        self.assertFalse(payload["selected_action_count_consistency_verified"])
        self.assertFalse(payload["legal_but_unselected_consistency_verified"])
        self.assertFalse(payload["exposure_matrix_internal_consistency_verified"])
        self.assertEqual(payload["legality_evidence_verified"]["source_feature"], "048-legality-evidence-expansion")
        self.assertTrue(payload["legality_evidence_verified"]["exposure_matrix_unblocked"])
        self.assertEqual(payload["selected_action_family_evidence_status"], "unavailable")
        self.assertEqual(payload["per_action_outcome_evidence_status"], "unavailable")
        self.assertFalse(payload["legal_vs_selected_action_matrix"]["matrix_complete"])
        self.assertFalse(payload["legal_vs_selected_action_matrix"]["trace_backed"])

    def test_prior_feature_gates_include_043_through_048(self) -> None:
        report = build_exposure_matrix_paper_mechanism_report()
        features = [entry["feature"] for entry in report.prior_feature_gates_verified if entry.get("verified") is True]
        self.assertEqual(features, ["037", "038", "039", "040", "041", "042", "043", "044", "045", "046", "047", "048"])


if __name__ == "__main__":
    unittest.main()
