from __future__ import annotations

import unittest

from src.analysis.campaign_execution_engine.report import build_feature_078_report, render_feature_078_report


class CampaignExecutionEngineIntegrationReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = build_feature_078_report()

    def test_feature_076_and_077_contracts_are_consumed(self) -> None:
        self.assertTrue(self.report.passed)
        self.assertIn("Feature 076 passed: True", self.report.validation_summary)
        self.assertIn("Feature 077 campaign contract consumed from config constants.", self.report.validation_summary)
        self.assertEqual(self.report.dependency_features, ("076-combined-baseline-proposed-comparative-readiness", "077-experimental-campaign-readiness"))

    def test_combined_matrix_size_is_441_times_seed_count(self) -> None:
        self.assertEqual(self.report.actual_row_count, 441 * self.report.seed_count)
        self.assertEqual(self.report.expected_row_count, self.report.actual_row_count)

    def test_rendered_report_contains_source_and_boundary_evidence(self) -> None:
        rendered = render_feature_078_report(self.report)
        self.assertIn("Feature 076 readiness rows are consumed as the action-bound execution substrate.", rendered)
        self.assertIn("Feature 077 campaign dimensions are consumed as the execution contract.", rendered)
        self.assertIn("No training claim is made.", rendered)
        self.assertIn("No superiority claim is made.", rendered)
        self.assertIn("No final evaluation claim is made.", rendered)
        self.assertIn("No statistical significance claim is made.", rendered)
        self.assertIn("No full paper reproduction claim is made.", rendered)
        self.assertIn("No statistical summary claim is made.", rendered)
        self.assertIn("No ranking claim is made.", rendered)
        self.assertIn("No winner claim is made.", rendered)
        self.assertNotIn("winner:", rendered.lower())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
