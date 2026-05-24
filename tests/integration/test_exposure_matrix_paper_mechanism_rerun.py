from __future__ import annotations

import unittest
from pathlib import Path

from src.analysis.exposure_matrix_paper_mechanism_rerun_with_outcome_evidence import build_exposure_matrix_paper_mechanism_rerun_report


class ExposureMatrixPaperMechanismRerunIntegrationTests(unittest.TestCase):
    def test_committed_prior_artifacts_are_present(self) -> None:
        for path in (
            "artifacts/analysis/legality-evidence-expansion/legality-evidence-report.json",
            "artifacts/analysis/exposure-matrix-paper-mechanism-alignment/exposure-matrix-paper-mechanism-report.json",
            "artifacts/analysis/selected-action-family-per-action-outcome-evidence/selected-action-family-outcome-evidence-report.json",
            "artifacts/analysis/passive-selected-action-trace-repair/passive-selected-action-trace-repair-report.json",
            "artifacts/analysis/selected-action-outcome-evidence-rerun/selected-action-outcome-evidence-rerun-report.json",
        ):
            self.assertTrue(Path(path).exists(), path)

    def test_report_is_deterministic_from_committed_inputs(self) -> None:
        first = build_exposure_matrix_paper_mechanism_rerun_report().to_dict()
        second = build_exposure_matrix_paper_mechanism_rerun_report().to_dict()
        self.assertEqual(first["final_verdict"], second["final_verdict"])
        self.assertEqual(first["remaining_blockers"], second["remaining_blockers"])
        self.assertEqual(first["recommended_next_feature"], second["recommended_next_feature"])


if __name__ == "__main__":
    unittest.main()
