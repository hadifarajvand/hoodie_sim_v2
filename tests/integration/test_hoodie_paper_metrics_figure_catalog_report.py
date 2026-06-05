from __future__ import annotations

import json
from pathlib import Path
import unittest

from src.analysis.hoodie_paper_metrics_figure_catalog.config import ARTIFACT_DIR
from src.analysis.hoodie_paper_metrics_figure_catalog.runner import generate_artifacts, validate_artifacts


class HoodiePaperMetricsFigureCatalogIntegrationTests(unittest.TestCase):
    def test_generate_and_validate(self) -> None:
        report = generate_artifacts(ARTIFACT_DIR)
        self.assertEqual(report.verdict, "paper_metrics_catalog_partial")
        validated = validate_artifacts(ARTIFACT_DIR)
        self.assertEqual(validated.verdict, "paper_metrics_catalog_partial")

    def test_feature_089_artifact_manifest_contains_required_files(self) -> None:
        report_path = ARTIFACT_DIR / "feature_089_report.json"
        self.assertTrue(report_path.exists())
        self.assertTrue((ARTIFACT_DIR / "figure_10_output_audit.json").exists())
        self.assertTrue((ARTIFACT_DIR / "figure_10_output_audit.md").exists())
        self.assertTrue((ARTIFACT_DIR / "figure_10_analysis_summary.json").exists())
        self.assertTrue((ARTIFACT_DIR / "figure_10_analysis_summary.md").exists())
        self.assertTrue((ARTIFACT_DIR / "feature_089_completion_report.json").exists())
        self.assertTrue((ARTIFACT_DIR / "feature_089_completion_report.md").exists())
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["figures_cataloged"], 14)
        self.assertEqual(payload["metrics_cataloged"], 6)
        self.assertEqual(payload["simulator_output_requirements"], 14)
        self.assertIn("Figure 10a", payload["ready_now_figures"])
        self.assertNotIn("Figure 9a", payload["ready_now_figures"])
        self.assertIn("Figure 9a", payload["blocked_figures"])
        self.assertIn("Figure 9e", payload["blocked_figures"])
        self.assertIn("Figure 8a", payload["future_required_figures"])
        self.assertIn("Figure 8b", payload["future_required_figures"])
        self.assertIn("Figure 11", payload["future_required_figures"])
        audit_payload = json.loads((ARTIFACT_DIR / "figure_10_output_audit.json").read_text(encoding="utf-8"))
        self.assertEqual(len(audit_payload), 6)
        self.assertTrue(all(row["audit_status"] == "pass" for row in audit_payload))
        completion_payload = json.loads((ARTIFACT_DIR / "feature_089_completion_report.json").read_text(encoding="utf-8"))
        self.assertEqual(completion_payload["completion_status"], "complete")
        self.assertEqual(completion_payload["blocked_figures"], ["Figure 9a", "Figure 9b", "Figure 9c", "Figure 9d", "Figure 9e"])
