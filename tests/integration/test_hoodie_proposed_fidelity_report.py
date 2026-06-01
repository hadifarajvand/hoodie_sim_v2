from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.analysis.hoodie_proposed_fidelity.report import build_feature_081_report, render_feature_081_report, write_feature_081_report


class HoodieProposedFidelityReportIntegrationTests(unittest.TestCase):
    def test_rendered_report_includes_matrix_and_repair_plan(self) -> None:
        report = build_feature_081_report()
        rendered = render_feature_081_report(report)
        self.assertIn("Feature 081 HOODIE Proposed Method Fidelity Extraction Report", rendered)
        self.assertIn("system_model", rendered)
        self.assertIn("dqn_training", rendered)
        self.assertIn("pubsub_recovery", rendered)
        self.assertIn("HOODIE_PROPOSED", rendered)
        self.assertNotIn("PROPOSED_DCQ", rendered)
        self.assertNotIn("thesis", rendered.lower())
        self.assertNotIn("deadline-aware", rendered.lower())

    def test_write_feature_081_report_emits_markdown_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = write_feature_081_report(Path(tmpdir))
            self.assertTrue(output.exists())
            self.assertTrue((Path(tmpdir) / "feature-081-hoodie-proposed-method-fidelity-extraction-report.json").exists())
            self.assertIn("hoodie-proposed-method-fidelity-extraction-report", output.name)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
