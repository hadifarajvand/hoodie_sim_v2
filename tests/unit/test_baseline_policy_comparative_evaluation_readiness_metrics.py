from __future__ import annotations

import unittest

from src.analysis.baseline_policy_comparative_evaluation_readiness.report import (
    build_feature_074_report,
    build_policy_scenario_comparisons,
    compute_policy_aggregate_metrics,
)


class BaselinePolicyComparativeEvaluationReadinessMetricsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = build_feature_074_report()
        self.comparisons = build_policy_scenario_comparisons()

    def test_policy_scenario_metrics_include_required_fields(self) -> None:
        comparison = next(
            item
            for item in self.comparisons
            if item.policy_id == "FLC" and item.scenario_id == "light_load_no_deadline_pressure"
        )
        metrics = comparison.metrics
        self.assertEqual(metrics.completed_count, 1)
        self.assertEqual(metrics.dropped_timeout_count, 0)
        self.assertEqual(metrics.dropped_unavailable_count, 0)
        self.assertEqual(metrics.deadline_violation_count, 0)
        self.assertEqual(metrics.illegal_action_rejection_count, 0)
        self.assertEqual(metrics.average_delay, 3.0)
        self.assertEqual(metrics.average_reward, -3.0)
        self.assertEqual(metrics.paper_mode_success_count, 1)
        self.assertFalse(metrics.compatibility_mode_used)
        self.assertEqual(comparison.policy_action_family, "fixed-local / local-first family")
        self.assertTrue(comparison.policy_decision_trace_present)

    def test_aggregate_metrics_match_the_scenario_rows_for_each_policy(self) -> None:
        for policy_id in {"FLC", "VO", "HO", "RO", "BCO", "MLEO"}:
            with self.subTest(policy_id=policy_id):
                rows = [comparison for comparison in self.comparisons if comparison.policy_id == policy_id]
                aggregate = compute_policy_aggregate_metrics(policy_id, rows)
                self.assertEqual(aggregate.scenario_count, 7)
                self.assertEqual(aggregate.completed_count, sum(row.metrics.completed_count for row in rows))
                self.assertEqual(aggregate.dropped_timeout_count, sum(row.metrics.dropped_timeout_count for row in rows))
                self.assertEqual(aggregate.dropped_unavailable_count, sum(row.metrics.dropped_unavailable_count for row in rows))
                self.assertEqual(aggregate.deadline_violation_count, sum(row.metrics.deadline_violation_count for row in rows))
                self.assertEqual(aggregate.illegal_action_rejection_count, sum(row.metrics.illegal_action_rejection_count for row in rows))
                self.assertEqual(aggregate.mean_delay, sum(row.metrics.average_delay for row in rows) / len(rows))
                self.assertEqual(aggregate.mean_reward, sum(row.metrics.average_reward for row in rows) / len(rows))
                self.assertFalse(aggregate.compatibility_mode_used)

    def test_compatibility_mode_is_not_used_in_default_comparison(self) -> None:
        self.assertTrue(all(not comparison.compatibility_mode_used for comparison in self.comparisons))
        self.assertTrue(all(not aggregate.compatibility_mode_used for aggregate in self.report.policy_aggregate_metrics))
        self.assertTrue(self.report.passed)


if __name__ == "__main__":
    unittest.main()
