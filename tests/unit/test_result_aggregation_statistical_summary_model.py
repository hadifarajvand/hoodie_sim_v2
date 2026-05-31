from __future__ import annotations

from dataclasses import replace
import unittest

from src.analysis.result_aggregation_statistical_summary.model import (
    AggregationReport,
    ComparativeAggregate,
    MetricSummary,
)
from src.analysis.result_aggregation_statistical_summary.report import build_feature_079_report


class ResultAggregationStatisticalSummaryModelTests(unittest.TestCase):
    def test_metric_summary_rejects_zero_count(self) -> None:
        with self.assertRaises(ValueError):
            MetricSummary(
                metric_name="completion_rate",
                mean=0.1,
                std=0.0,
                min=0.1,
                max=0.1,
                count=0,
                ci95_low=0.1,
                ci95_high=0.1,
            )

    def test_policy_aggregate_requires_all_metrics(self) -> None:
        report = build_feature_079_report()
        policy_aggregate = report.policy_aggregates[0]
        with self.assertRaises(ValueError):
            replace(policy_aggregate, metric_summaries=policy_aggregate.metric_summaries[:-1])

    def test_comparative_aggregate_requires_all_policies_for_non_policy_groupings(self) -> None:
        report = build_feature_079_report()
        comparative_aggregate = next(aggregate for aggregate in report.comparative_aggregates if aggregate.grouping_type == "policy_scenario")
        with self.assertRaises(ValueError):
            replace(comparative_aggregate, policy_aggregates=(report.policy_aggregates[0],))

    def test_aggregation_report_rejects_missing_policy(self) -> None:
        report = build_feature_079_report()
        with self.assertRaises(ValueError):
            replace(report, policy_aggregates=report.policy_aggregates[1:])

    def test_aggregation_report_rejects_missing_scenario(self) -> None:
        report = build_feature_079_report()
        missing_scenario = tuple(
            aggregate
            for aggregate in report.comparative_aggregates
            if not (aggregate.grouping_type == "policy_scenario" and aggregate.grouping_key.endswith("light_load_no_deadline_pressure"))
        )
        with self.assertRaises(ValueError):
            replace(report, comparative_aggregates=missing_scenario)

    def test_aggregation_report_rejects_missing_claim_boundary(self) -> None:
        report = build_feature_079_report()
        with self.assertRaises(ValueError):
            replace(report, claim_boundary=())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
