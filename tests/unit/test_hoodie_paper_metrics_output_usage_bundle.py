from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.analysis.hoodie_paper_metrics_figure_catalog import generate_output_usage_bundle, validate_output_usage_bundle
from src.analysis.hoodie_paper_metrics_figure_catalog.config import ARTIFACT_DIR


class HoodiePaperMetricsOutputUsageBundleTests(unittest.TestCase):
    def test_generate_bundle_builds_expected_files(self) -> None:
        with TemporaryDirectory(prefix="feature_089_bundle_") as tmp_dir:
            bundle_dir = Path(tmp_dir)
            manifest = generate_output_usage_bundle(ARTIFACT_DIR, bundle_dir)
            self.assertEqual(manifest["verdict"], "feature_089_output_bundle_ready")
            self.assertTrue(manifest["validation"]["figure_10_present"])
            self.assertTrue(manifest["validation"]["figure_9_present"])
            self.assertTrue(manifest["validation"]["gated_status_present"])
            self.assertTrue(manifest["validation"]["claim_boundary_populated"])
            self.assertTrue(manifest["validation"]["no_output_sync_tuning"])
            self.assertEqual(manifest["row_counts"]["figure_10"], 266)
            self.assertEqual(manifest["row_counts"]["figure_9"], 78)
            self.assertEqual(manifest["row_counts"]["index"], 14)

            index_payload = json.loads((bundle_dir / "figure_output_index.json").read_text(encoding="utf-8"))
            self.assertEqual(len(index_payload), 14)
            self.assertEqual(index_payload[0]["figure_id"], "Figure 10a")
            self.assertEqual(index_payload[6]["figure_id"], "Figure 9a")
            self.assertEqual(index_payload[-1]["figure_id"], "Figure 11")
            self.assertTrue(all(entry["claim_boundary"] for entry in index_payload))
            self.assertEqual(index_payload[6]["status"], "generated_with_approximation")
            self.assertEqual(index_payload[12]["status"], "not_generated_training_required")

            figure_10_payload = json.loads((bundle_dir / "figure_10_plot_ready_combined.json").read_text(encoding="utf-8"))
            self.assertEqual(len(figure_10_payload), 266)
            self.assertIn("paper_style_value", figure_10_payload[0])
            self.assertIn("value_units", figure_10_payload[0])
            self.assertTrue(all(row["claim_boundary"] for row in figure_10_payload))

            figure_9_payload = json.loads((bundle_dir / "figure_9_plot_ready_combined.json").read_text(encoding="utf-8"))
            self.assertEqual(len(figure_9_payload), 78)
            self.assertTrue(all(row["support_status"] == "generated_with_approximation" for row in figure_9_payload))
            self.assertTrue(all(row["approximation_note"] for row in figure_9_payload))
            self.assertTrue(all(row["claim_boundary"] for row in figure_9_payload))

            validated = validate_output_usage_bundle(ARTIFACT_DIR, bundle_dir)
            self.assertEqual(validated["verdict"], "feature_089_output_bundle_ready")

    def test_gated_rows_remain_gated(self) -> None:
        with TemporaryDirectory(prefix="feature_089_bundle_") as tmp_dir:
            bundle_dir = Path(tmp_dir)
            generate_output_usage_bundle(ARTIFACT_DIR, bundle_dir)
            index_payload = json.loads((bundle_dir / "figure_output_index.json").read_text(encoding="utf-8"))
            gated = {entry["figure_id"]: entry for entry in index_payload if entry["figure_id"] in {"Figure 8a", "Figure 8b", "Figure 11"}}
            self.assertEqual(gated["Figure 8a"]["plot_ready_available"], False)
            self.assertEqual(gated["Figure 8b"]["plot_ready_available"], False)
            self.assertEqual(gated["Figure 11"]["plot_ready_available"], False)
            self.assertIn("Feature 080 prepares HOODIE_PROPOSED", gated["Figure 8a"]["claim_boundary"][0])
            self.assertIn("Feature 086 approximations remain in force", gated["Figure 11"]["claim_boundary"][-1])
