from __future__ import annotations

import unittest

from src.analysis.hoodie_paper_metrics_figure_catalog import generate_output_usage_bundle, validate_output_usage_bundle
from src.analysis.hoodie_paper_metrics_figure_catalog.config import ARTIFACT_DIR


class HoodiePaperMetricsOutputUsageBundleIntegrationTests(unittest.TestCase):
    def test_generate_bundle_into_artifact_dir(self) -> None:
        manifest = generate_output_usage_bundle(ARTIFACT_DIR)
        self.assertEqual(manifest["verdict"], "feature_089_output_bundle_ready")
        validated = validate_output_usage_bundle(ARTIFACT_DIR)
        self.assertEqual(validated["verdict"], "feature_089_output_bundle_ready")
        report_text = (ARTIFACT_DIR / "output_usage_bundle" / "output_usage_report.md").read_text(encoding="utf-8")
        self.assertIn("feature_089_output_bundle_ready", report_text)
        self.assertIn("Figure 9 remains approximation-tagged", report_text)

    def test_bundle_files_exist_in_artifact_dir(self) -> None:
        bundle_dir = ARTIFACT_DIR / "output_usage_bundle"
        generate_output_usage_bundle(ARTIFACT_DIR, bundle_dir)
        expected_files = {
            "README.md",
            "figure_output_index.json",
            "figure_output_index.md",
            "figure_10_plot_ready_combined.csv",
            "figure_10_plot_ready_combined.json",
            "figure_9_plot_ready_combined.csv",
            "figure_9_plot_ready_combined.json",
            "figure_10_analysis_digest.md",
            "figure_9_analysis_digest.md",
            "gated_figures_status_digest.md",
            "claim_boundary_digest.md",
            "output_usage_manifest.json",
            "output_usage_report.md",
        }
        self.assertTrue(expected_files.issubset({path.name for path in bundle_dir.iterdir()}))
