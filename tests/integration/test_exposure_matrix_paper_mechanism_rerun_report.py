from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.exposure_matrix_paper_mechanism_rerun_with_outcome_evidence import (
    build_exposure_matrix_paper_mechanism_rerun_report,
    write_exposure_matrix_paper_mechanism_rerun_report,
)


class ExposureMatrixPaperMechanismRerunReportIntegrationTests(unittest.TestCase):
    def test_report_write_outputs_json_and_markdown(self) -> None:
        report = build_exposure_matrix_paper_mechanism_rerun_report()
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path, md_path = write_exposure_matrix_paper_mechanism_rerun_report(report, output_dir=tmpdir)
            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())
            payload = json.loads(Path(json_path).read_text(encoding="utf-8"))
            self.assertEqual(payload["feature_id"], "053-exposure-matrix-paper-mechanism-rerun-with-outcome-evidence")
            self.assertEqual(payload["final_verdict"], "paper_mechanism_alignment_ready_for_training_contract")
            self.assertIn("behavior_equivalence_summary", payload)
            self.assertIn("paper_mechanism_alignment_ready", payload)

    def test_report_matches_builder_payload(self) -> None:
        report = build_exposure_matrix_paper_mechanism_rerun_report()
        payload = report.to_dict()
        self.assertEqual(payload["feature_052_readiness_verified"], True)
        self.assertEqual(payload["feature_052_trace_readiness_verified"], True)
        self.assertEqual(payload["paper_mechanism_alignment_ready"], True)
        self.assertEqual(payload["recommended_next_feature"], "Feature 054 — Training Readiness Contract")


if __name__ == "__main__":
    unittest.main()
