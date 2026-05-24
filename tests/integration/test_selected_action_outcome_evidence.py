from __future__ import annotations

import json
from pathlib import Path
import unittest

from src.analysis.selected_action_family_per_action_outcome_evidence import build_selected_action_outcome_evidence_report


class SelectedActionOutcomeEvidenceIntegrationTest(unittest.TestCase):
    def test_report_uses_committed_artifacts_only(self) -> None:
        payload = build_selected_action_outcome_evidence_report().to_dict()
        self.assertEqual(payload["feature_id"], "050-selected-action-family-per-action-outcome-evidence")
        self.assertEqual(payload["evidence_population_summary"]["selected_action_family_evidence_source"], "artifacts/analysis/exposure-matrix-paper-mechanism-alignment/exposure-matrix-paper-mechanism-report.json")
        legality = json.loads(Path("artifacts/analysis/legality-evidence-expansion/legality-evidence-report.json").read_text(encoding="utf-8"))
        exposure = json.loads(Path("artifacts/analysis/exposure-matrix-paper-mechanism-alignment/exposure-matrix-paper-mechanism-report.json").read_text(encoding="utf-8"))
        self.assertEqual(legality["feature_id"], "048-legality-evidence-expansion")
        self.assertIn("legal_evidence_coverage_ratio", legality)
        self.assertIn("legal_evidence_coverage_ratio", legality["legality_evidence_coverage_summary"])
        self.assertEqual(legality["legal_evidence_coverage_ratio"], legality["legality_evidence_coverage_summary"]["legal_evidence_coverage_ratio"])
        self.assertTrue(legality["behavior_equivalence_summary"]["passed"])
        self.assertTrue(legality["no_runtime_repair_performed"])
        self.assertTrue(legality["no_training_started"])
        self.assertTrue(legality["no_paper_reproduction_claim"])
        self.assertEqual(exposure["feature_id"], "049-exposure-matrix-paper-mechanism-alignment")
        self.assertEqual(exposure["final_verdict"], "insufficient_legality_or_trace_evidence")
        self.assertEqual(exposure["selected_action_family_evidence_status"], "unavailable")
        self.assertEqual(exposure["per_action_outcome_evidence_status"], "unavailable")
        self.assertFalse(exposure["exposure_matrix_internal_consistency_verified"])
        self.assertTrue(exposure["recommended_next_feature"])
        self.assertTrue(exposure["no_runtime_repair_performed"])
        self.assertTrue(exposure["no_training_started"])
        self.assertTrue(exposure["no_paper_reproduction_claim"])


if __name__ == "__main__":
    unittest.main()
