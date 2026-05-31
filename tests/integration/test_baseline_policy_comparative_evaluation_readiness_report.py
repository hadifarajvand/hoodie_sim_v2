from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.analysis.baseline_policy_comparative_evaluation_readiness.report import (
    build_feature_074_report,
    render_feature_074_report,
    write_feature_074_report,
)


class BaselinePolicyComparativeEvaluationReadinessReportIntegrationTests(unittest.TestCase):
    def test_rendered_report_mentions_required_policies_scenarios_and_claim_boundary(self) -> None:
        report = build_feature_074_report()
        rendered = render_feature_074_report(report)
        self.assertIn("Feature 074 - Baseline Policy Comparative Evaluation Readiness", rendered)
        self.assertIn("baseline_policy_comparative_evaluation_readiness_ready", rendered)
        self.assertIn("FLC", rendered)
        self.assertIn("VO", rendered)
        self.assertIn("HO", rendered)
        self.assertIn("RO", rendered)
        self.assertIn("BCO", rendered)
        self.assertIn("MLEO", rendered)
        self.assertIn("light_load_no_deadline_pressure", rendered)
        self.assertIn("tight_deadline_pressure", rendered)
        self.assertIn("legal_horizontal_offload", rendered)
        self.assertIn("illegal_horizontal_destination_attempt", rendered)
        self.assertIn("cloud_vertical_fallback", rendered)
        self.assertIn("timeout_drop_case", rendered)
        self.assertIn("mixed_local_horizontal_cloud_candidates", rendered)
        self.assertIn("No final evaluation claim is made.", rendered)
        self.assertIn("No performance superiority claim is made.", rendered)
        self.assertIn("No statistical significance claim is made.", rendered)
        self.assertIn("No full paper reproduction claim is made.", rendered)
        self.assertIn("Feature 073 controlled scenarios are consumed", rendered)
        self.assertIn("Feature 072 report is consumed", rendered)

    def test_write_feature_074_report_emits_markdown_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = write_feature_074_report(Path(tmpdir))
            self.assertTrue(output.exists())
            self.assertTrue((Path(tmpdir) / "feature-074-baseline-policy-comparative-evaluation-readiness-report.json").exists())
            markdown = output.read_text(encoding="utf-8")
            self.assertIn("baseline_policy_comparative_evaluation_readiness_ready", markdown)


if __name__ == "__main__":
    unittest.main()
