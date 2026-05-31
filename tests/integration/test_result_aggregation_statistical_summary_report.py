from __future__ import annotations

import unittest

from src.analysis.result_aggregation_statistical_summary.report import (
    build_feature_079_report,
    render_feature_079_report,
)


class ResultAggregationStatisticalSummaryIntegrationReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = build_feature_079_report()

    def test_feature_078_report_is_consumed(self) -> None:
        self.assertTrue(self.report.passed)
        self.assertIn("Feature 078 status: campaign_execution_engine_ready", self.report.validation_summary)
        self.assertIn("Feature 078 passed: True", self.report.validation_summary)
        self.assertEqual(self.report.dependency_features, ("078-campaign-execution-engine", "077-experimental-campaign-readiness"))

    def test_rendered_report_exposes_policy_coverage_and_claim_boundary(self) -> None:
        rendered = render_feature_079_report(self.report)
        for policy_id in ("FLC", "VO", "HO", "RO", "BCO", "MLEO", "PROPOSED_DCQ"):
            self.assertIn(policy_id, rendered)
        self.assertIn("Feature 078 raw execution rows are consumed as input.", rendered)
        self.assertIn("No runtime execution occurs in Feature 079.", rendered)
        self.assertIn("No ranking claim is made.", rendered)
        self.assertIn("No winner claim is made.", rendered)
        self.assertIn("No superiority claim is made.", rendered)
        self.assertIn("No final evaluation claim is made.", rendered)
        self.assertIn("No statistical significance claim is made.", rendered)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
