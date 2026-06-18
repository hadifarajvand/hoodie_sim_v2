from __future__ import annotations

import unittest
from unittest.mock import patch

from src.analysis.exposure_matrix_paper_mechanism_alignment import build_exposure_matrix_paper_mechanism_report


class ExposureMatrixPaperMechanismSchemaTests(unittest.TestCase):
    def test_report_schema_includes_required_sections(self) -> None:
        with patch("src.analysis.exposure_matrix_paper_mechanism_alignment.runner._tracked_dirty_paths", return_value=[]):
            report = build_exposure_matrix_paper_mechanism_report()
        payload = report.to_dict()
        self.assertEqual(payload["feature_id"], "049-exposure-matrix-paper-mechanism-alignment")
        for key in (
            "prerequisite_tags_verified",
            "prior_feature_gates_verified",
            "legality_evidence_verified",
            "exposure_matrix_rerun_summary",
            "legal_vs_selected_action_matrix",
            "per_strategy_seed_matrix",
            "per_action_outcome_matrix",
            "selected_illegal_action_summary",
            "selected_action_family_evidence_status",
            "selected_action_count_consistency_verified",
            "legal_but_unselected_consistency_verified",
            "per_action_outcome_evidence_status",
            "exposure_matrix_internal_consistency_verified",
            "observation_vector_audit",
            "paper_formula_unit_audit",
            "runtime_semantic_drift_check",
            "training_readiness_decision",
            "recommended_next_feature",
            "final_verdict",
        ):
            self.assertIn(key, payload)

    def test_observation_audit_schema_has_required_fields(self) -> None:
        with patch("src.analysis.exposure_matrix_paper_mechanism_alignment.runner._tracked_dirty_paths", return_value=[]):
            report = build_exposure_matrix_paper_mechanism_report()
        audit = report.to_dict()["observation_vector_audit"]
        self.assertIn("fields", audit)
        self.assertIn("blocking_fields", audit)
        self.assertIn("passed", audit)
        self.assertIn("evidence_sources", audit)

    def test_formula_audit_schema_has_required_fields(self) -> None:
        with patch("src.analysis.exposure_matrix_paper_mechanism_alignment.runner._tracked_dirty_paths", return_value=[]):
            report = build_exposure_matrix_paper_mechanism_report()
        audit = report.to_dict()["paper_formula_unit_audit"]
        self.assertIn("items", audit)
        self.assertIn("passed", audit)
        self.assertIn("blocking_items", audit)
        self.assertIn("evidence_sources", audit)

    def test_exposure_matrix_rerun_summary_includes_consistency_fields(self) -> None:
        with patch("src.analysis.exposure_matrix_paper_mechanism_alignment.runner._tracked_dirty_paths", return_value=[]):
            report = build_exposure_matrix_paper_mechanism_report()
        summary = report.to_dict()["exposure_matrix_rerun_summary"]
        for key in (
            "selected_action_family_evidence_status",
            "selected_action_count_consistency_verified",
            "legal_but_unselected_consistency_verified",
            "per_action_outcome_evidence_status",
            "exposure_matrix_internal_consistency_verified",
        ):
            self.assertIn(key, summary)


if __name__ == "__main__":
    unittest.main()
