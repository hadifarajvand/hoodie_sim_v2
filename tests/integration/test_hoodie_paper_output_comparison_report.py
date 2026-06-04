from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from src.analysis.hoodie_paper_output_comparison.runner import generate_artifacts, validate_artifacts


class HoodiePaperOutputComparisonReportIntegrationTests(unittest.TestCase):
    def test_generate_and_validate_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_dir = Path(tmpdir)
            report = generate_artifacts(artifact_dir)
            self.assertIn(report.verdict, {"paper_output_comparison_ready", "paper_output_comparison_partial", "paper_output_comparison_blocked"})
            validated = validate_artifacts(artifact_dir)
            self.assertEqual(validated.verdict, report.verdict)
            required = {
                "paper_output_extraction.json",
                "paper_output_extraction.md",
                "simulator_output_inventory.json",
                "simulator_output_inventory.md",
                "metric_alignment_matrix.json",
                "metric_alignment_matrix.md",
                "comparison_by_metric.json",
                "comparison_by_metric.csv",
                "comparison_by_policy.json",
                "comparison_by_policy.csv",
                "figure_comparison_coverage.json",
                "ranking_agreement.json",
                "feature_087_paper_output_comparison_report.json",
                "feature_087_paper_output_comparison_report.md",
            }
            self.assertTrue(required.issubset({path.name for path in artifact_dir.iterdir()}))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

