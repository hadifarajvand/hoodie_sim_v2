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
        generate_artifacts(ARTIFACT_DIR)
        report_path = ARTIFACT_DIR / "feature_089_report.json"
        self.assertTrue(report_path.exists())
        self.assertTrue((ARTIFACT_DIR / "figure_10_output_audit.json").exists())
        self.assertTrue((ARTIFACT_DIR / "figure_10_output_audit.md").exists())
        self.assertTrue((ARTIFACT_DIR / "figure_10_analysis_summary.json").exists())
        self.assertTrue((ARTIFACT_DIR / "figure_10_analysis_summary.md").exists())
        self.assertTrue((ARTIFACT_DIR / "feature_089_completion_report.json").exists())
        self.assertTrue((ARTIFACT_DIR / "feature_089_completion_report.md").exists())
        self.assertTrue((ARTIFACT_DIR / "figure_10_trend_analysis.json").exists())
        self.assertTrue((ARTIFACT_DIR / "figure_10_ranking_analysis.json").exists())
        self.assertTrue((ARTIFACT_DIR / "figure_10_paper_claim_alignment.json").exists())
        self.assertTrue((ARTIFACT_DIR / "figure_10_comparison_analysis_report.json").exists())
        self.assertTrue((ARTIFACT_DIR / "remaining_figure_outputs_report.json").exists())
        self.assertTrue((ARTIFACT_DIR / "figure_8a_learning_rate_convergence_status.json").exists())
        self.assertTrue((ARTIFACT_DIR / "figure_8b_discount_factor_convergence_status.json").exists())
        self.assertTrue((ARTIFACT_DIR / "figure_11_lstm_ablation_status.json").exists())
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
        comparison_payload = json.loads((ARTIFACT_DIR / "figure_10_comparison_analysis_report.json").read_text(encoding="utf-8"))
        self.assertEqual(comparison_payload["verdict"], "figure_10_comparison_analysis_partial")
        self.assertFalse(comparison_payload["paper_numeric_digitization_performed"])
        remaining_payload = json.loads((ARTIFACT_DIR / "remaining_figure_outputs_report.json").read_text(encoding="utf-8"))
        self.assertEqual(remaining_payload["verdict"], "feature_089_remaining_outputs_partial")
        self.assertTrue(remaining_payload["no_output_sync_tuning"])
        self.assertEqual(remaining_payload["figure_9_status_by_figure"]["Figure 9a"]["status"], "generated_with_approximation")
        self.assertEqual(remaining_payload["figure_9_status_by_figure"]["Figure 9b"]["status"], "generated_with_approximation")
        self.assertEqual(remaining_payload["figure_9_status_by_figure"]["Figure 9c"]["status"], "generated_with_approximation")
        self.assertEqual(remaining_payload["figure_9_status_by_figure"]["Figure 9d"]["status"], "generated_with_approximation")
        self.assertEqual(remaining_payload["figure_9_status_by_figure"]["Figure 9e"]["status"], "generated_with_approximation")
        self.assertEqual(remaining_payload["figure_8_status_by_figure"]["Figure 8a"]["support_status"], "not_generated_training_required")
        self.assertEqual(remaining_payload["figure_8_status_by_figure"]["Figure 8b"]["support_status"], "not_generated_training_required")
        self.assertEqual(remaining_payload["figure_11_status"]["support_status"], "not_generated_lstm_training_required")
