from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.analysis.legality_evidence_expansion import build_legality_evidence_report, write_legality_evidence_report


class LegalityEvidenceReportIntegrationTests(unittest.TestCase):
    def test_feature_047_committed_artifact_prerequisite(self) -> None:
        payload = json.loads(Path("artifacts/analysis/exposure-matrix-review/exposure-matrix-report.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["feature_id"], "047-exposure-matrix-review")
        self.assertEqual(payload["final_verdict"], "exposure_matrix_incomplete_requires_legality_evidence")
        self.assertEqual(payload["recommended_next_feature"], "legality evidence expansion before Feature 048")
        self.assertEqual(payload["legal_action_evidence_source"], "unavailable_in_committed_artifacts")
        self.assertEqual(payload["legal_action_evidence_coverage_ratio"], 0.0)
        self.assertIsNone(payload["illegal_action_summary"]["selected_illegal_action_count"])
        self.assertEqual(
            [entry["feature"] for entry in payload["prior_feature_gates_verified"] if entry.get("verified") is True],
            ["037", "038", "039", "040", "041", "042", "043", "044", "045", "046"],
        )
        self.assertTrue(payload["no_runtime_repair_performed"])
        self.assertTrue(payload["no_training_started"])
        self.assertTrue(payload["no_paper_reproduction_claim"])

    def test_report_write_outputs_json_and_markdown(self) -> None:
        report = build_legality_evidence_report()
        with TemporaryDirectory() as tmpdir:
            json_path, md_path = write_legality_evidence_report(report, output_dir=tmpdir)
            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())
            payload = json.loads(Path(json_path).read_text(encoding="utf-8"))
            self.assertIn("legal_evidence_coverage_ratio", payload)
            self.assertIn("legal_evidence_coverage_ratio", payload["legality_evidence_coverage_summary"])
            self.assertEqual(payload["legal_evidence_coverage_ratio"], payload["legality_evidence_coverage_summary"]["legal_evidence_coverage_ratio"])


if __name__ == "__main__":
    unittest.main()
