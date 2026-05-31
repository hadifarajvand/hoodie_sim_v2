from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.analysis.combined_baseline_proposed_comparative_readiness.report import (
    build_feature_076_report,
    render_feature_076_report,
    write_feature_076_report,
)


class CombinedBaselineProposedComparativeReadinessReportIntegrationTests(unittest.TestCase):
    def test_combined_report_consumes_feature_074_and_feature_075_and_renders_scope_boundary(self) -> None:
        report = build_feature_076_report()
        rendered = render_feature_076_report(report)
        self.assertTrue(report.passed)
        self.assertEqual(len(report.rows), 49)
        self.assertEqual(sum(1 for row in report.rows if row.source_feature == "074"), 42)
        self.assertEqual(sum(1 for row in report.rows if row.source_feature == "075"), 7)
        self.assertIn("Feature 074 source report status", rendered)
        self.assertIn("Feature 075 source report status", rendered)
        self.assertIn("Feature 074 rows are consumed.", rendered)
        self.assertIn("Feature 075 rows are consumed.", rendered)
        self.assertIn("No training claim is made.", rendered)
        self.assertIn("No superiority claim is made.", rendered)
        self.assertIn("No final evaluation claim is made.", rendered)
        self.assertIn("No statistical significance claim is made.", rendered)
        self.assertIn("No full paper reproduction claim is made.", rendered)

    def test_write_feature_076_report_emits_markdown_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = write_feature_076_report(Path(tmpdir))
            self.assertTrue(output.exists())
            self.assertTrue((Path(tmpdir) / "feature-076-combined-baseline-proposed-comparative-readiness-report.json").exists())
            markdown = output.read_text(encoding="utf-8")
            self.assertIn("combined_baseline_proposed_comparative_readiness_ready", markdown)


if __name__ == "__main__":
    unittest.main()
