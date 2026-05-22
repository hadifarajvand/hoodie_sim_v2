from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.exposure_matrix_review import build_exposure_matrix_report
from src.analysis.exposure_matrix_review.report import write_exposure_matrix_report


class ExposureMatrixReportIntegrationTests(unittest.TestCase):
    def test_report_writes_json_and_markdown_artifacts(self) -> None:
        report = build_exposure_matrix_report()
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path, md_path = write_exposure_matrix_report(report, output_dir=tmpdir)
            self.assertTrue(Path(json_path).exists())
            self.assertTrue(Path(md_path).exists())
            payload = json.loads(Path(json_path).read_text(encoding="utf-8"))
            self.assertEqual(payload["feature_id"], "047-exposure-matrix-review")
            self.assertIn("illegal_action_summary", payload)
            self.assertIn("selected_illegal_action_count", payload["illegal_action_summary"])

    def test_report_fails_if_illegal_action_summary_missing(self) -> None:
        report = build_exposure_matrix_report()
        payload = report.to_dict()
        self.assertIn("illegal_action_summary", payload)
        self.assertIn("evidence_status", payload["illegal_action_summary"])
        self.assertEqual(payload["illegal_action_summary"]["evidence_status"], "unavailable")
        self.assertEqual(payload["illegal_action_summary"]["selected_illegal_action_examples"], [])

    def test_unavailable_legal_evidence_uses_null_not_fake_zero(self) -> None:
        report = build_exposure_matrix_report()
        illegal = report.illegal_action_summary.to_dict()
        self.assertIsNone(illegal["selected_illegal_action_count"])
        self.assertIsNone(illegal["selected_illegal_action_rate"])
        self.assertEqual(illegal["selected_illegal_action_examples"], [])


if __name__ == "__main__":
    unittest.main()
