from __future__ import annotations

import unittest

from src.analysis.exposure_matrix_paper_mechanism_alignment import build_exposure_matrix_paper_mechanism_report


class ExposureMatrixPaperMechanismSchemaTests(unittest.TestCase):
    def test_report_schema_includes_required_sections(self) -> None:
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
            "observation_vector_audit",
            "paper_formula_unit_audit",
            "runtime_semantic_drift_check",
            "training_readiness_decision",
            "recommended_next_feature",
            "final_verdict",
        ):
            self.assertIn(key, payload)

    def test_observation_audit_schema_has_required_fields(self) -> None:
        report = build_exposure_matrix_paper_mechanism_report()
        audit = report.to_dict()["observation_vector_audit"]
        self.assertIn("fields", audit)
        self.assertIn("blocking_fields", audit)
        self.assertIn("passed", audit)
        self.assertIn("evidence_sources", audit)

    def test_formula_audit_schema_has_required_fields(self) -> None:
        report = build_exposure_matrix_paper_mechanism_report()
        audit = report.to_dict()["paper_formula_unit_audit"]
        self.assertIn("items", audit)
        self.assertIn("passed", audit)
        self.assertIn("blocking_items", audit)
        self.assertIn("evidence_sources", audit)


if __name__ == "__main__":
    unittest.main()
