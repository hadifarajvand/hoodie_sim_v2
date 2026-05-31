from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch
import unittest

from src.analysis.result_aggregation_statistical_summary.config import READY_STATUS, REQUIRED_METRIC_NAMES, REQUIRED_POLICY_IDS, REQUIRED_SCENARIO_IDS
from src.analysis.result_aggregation_statistical_summary.report import (
    build_feature_079_report,
    render_feature_079_report,
)


class ResultAggregationStatisticalSummaryReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = build_feature_079_report()

    def test_report_is_ready_and_consumes_feature_078(self) -> None:
        self.assertEqual(self.report.status, READY_STATUS)
        self.assertTrue(self.report.passed)
        self.assertEqual(self.report.feature_id, "079-result-aggregation-statistical-summary")
        self.assertEqual(self.report.dependency_features, ("078-campaign-execution-engine", "077-experimental-campaign-readiness"))
        self.assertIn("Feature 078 status: campaign_execution_engine_ready", self.report.validation_summary)
        self.assertIn("Feature 078 passed: True", self.report.validation_summary)

    def test_all_policies_and_metrics_are_represented(self) -> None:
        self.assertEqual(len(self.report.policy_aggregates), len(REQUIRED_POLICY_IDS))
        self.assertEqual({aggregate.policy_id for aggregate in self.report.policy_aggregates}, set(REQUIRED_POLICY_IDS))
        self.assertTrue(all(len(aggregate.metric_summaries) == len(REQUIRED_METRIC_NAMES) for aggregate in self.report.policy_aggregates))
        self.assertTrue(all(summary.count > 0 for aggregate in self.report.policy_aggregates for summary in aggregate.metric_summaries))
        self.assertTrue(all(summary.ci95_low <= summary.mean <= summary.ci95_high for aggregate in self.report.policy_aggregates for summary in aggregate.metric_summaries))

    def test_comparative_aggregates_cover_all_required_groupings(self) -> None:
        self.assertEqual(len(self.report.comparative_aggregates), 29)
        counts = {
            grouping: sum(1 for aggregate in self.report.comparative_aggregates if aggregate.grouping_type == grouping)
            for grouping in ("policy", "policy_scenario", "policy_workload", "policy_deadline", "policy_workload_deadline")
        }
        self.assertEqual(counts["policy"], 7)
        self.assertEqual(counts["policy_scenario"], 7)
        self.assertEqual(counts["policy_workload"], 3)
        self.assertEqual(counts["policy_deadline"], 3)
        self.assertEqual(counts["policy_workload_deadline"], 9)
        self.assertTrue(all(aggregate.policy_aggregates for aggregate in self.report.comparative_aggregates))

    def test_rendered_report_contains_claim_boundary_and_no_overclaims(self) -> None:
        rendered = render_feature_079_report(self.report)
        self.assertIn("Feature 079 Result Aggregation Statistical Summary Report", rendered)
        self.assertIn("Feature 078 raw execution rows are consumed as input.", rendered)
        self.assertIn("No runtime execution occurs in Feature 079.", rendered)
        self.assertIn("No ranking or winner declaration is produced.", rendered)
        self.assertIn("No superiority, final evaluation, or statistical significance claim is made.", rendered)
        self.assertIn("No training claim is made.", rendered)
        self.assertIn("No ranking claim is made.", rendered)
        self.assertIn("No winner claim is made.", rendered)
        self.assertIn("No superiority claim is made.", rendered)
        self.assertIn("No final evaluation claim is made.", rendered)
        self.assertIn("No statistical significance claim is made.", rendered)

    def test_build_report_rejects_failed_feature_078_input(self) -> None:
        fake_feature_078 = SimpleNamespace(status="campaign_execution_engine_with_blockers", passed=False, result_rows=())
        with patch("src.analysis.result_aggregation_statistical_summary.report._feature_078_report", return_value=fake_feature_078):
            with self.assertRaises(ValueError):
                build_feature_079_report()


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
