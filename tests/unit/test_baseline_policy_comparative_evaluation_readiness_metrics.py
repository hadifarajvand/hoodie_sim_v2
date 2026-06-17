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

    def test_policy_scenario_metrics_include_required_fields_for_local_vertical_and_horizontal_paths(self) -> None:
        flc_light = next(
            item
            for item in self.comparisons
            if item.policy_id == "FLC" and item.scenario_id == "light_load_no_deadline_pressure"
        )
        vo_cloud = next(
            item
            for item in self.comparisons
            if item.policy_id == "VO" and item.scenario_id == "cloud_vertical_fallback"
        )
        ho_legal = next(
            item
            for item in self.comparisons
            if item.policy_id == "HO" and item.scenario_id == "legal_horizontal_offload"
        )

        self.assertEqual(flc_light.metrics.completed_count, 1)
        self.assertEqual(flc_light.metrics.dropped_timeout_count, 0)
        self.assertEqual(flc_light.metrics.dropped_unavailable_count, 0)
        self.assertEqual(flc_light.metrics.deadline_violation_count, 0)
        self.assertEqual(flc_light.metrics.illegal_action_rejection_count, 0)
        self.assertEqual(flc_light.metrics.average_delay, 3.0)
        self.assertEqual(flc_light.metrics.average_reward, -3.0)
        self.assertEqual(flc_light.metrics.paper_mode_success_count, 1)
        self.assertFalse(flc_light.metrics.compatibility_mode_used)
        self.assertEqual(flc_light.selected_action_family, "local")
        self.assertTrue(flc_light.action_bound_metrics_derived)

        self.assertEqual(vo_cloud.selected_action_family, "vertical")
        self.assertEqual(vo_cloud.metrics.completed_count, 1)
        self.assertEqual(vo_cloud.metrics.average_delay, 3.0)
        self.assertEqual(vo_cloud.metrics.average_reward, -3.0)
        self.assertTrue(vo_cloud.action_bound_metrics_derived)

        self.assertEqual(ho_legal.selected_action_family, "horizontal")
        self.assertEqual(ho_legal.metrics.completed_count, 1)
        self.assertEqual(ho_legal.metrics.average_delay, 4.0)
        self.assertEqual(ho_legal.metrics.average_reward, -5.0)
        self.assertTrue(ho_legal.action_bound_metrics_derived)

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
                self.assertEqual(aggregate.distinct_selected_action_families, tuple(sorted({row.selected_action_family for row in rows})))
                self.assertTrue(aggregate.action_bound_metrics_derived)
                self.assertFalse(aggregate.compatibility_mode_used)

    def test_no_metric_copy_from_feature_073_for_all_policies(self) -> None:
        ho_legal = next(
            item
            for item in self.comparisons
            if item.policy_id == "HO" and item.scenario_id == "legal_horizontal_offload"
        )
        flc_legal = next(
            item
            for item in self.comparisons
            if item.policy_id == "FLC" and item.scenario_id == "legal_horizontal_offload"
        )
        self.assertNotEqual(flc_legal.metrics.average_reward, ho_legal.metrics.average_reward)
        self.assertNotEqual(flc_legal.metrics.average_delay, ho_legal.metrics.average_delay)
        aggregate_signatures = {
            (
                aggregate.completed_count,
                aggregate.dropped_timeout_count,
                aggregate.dropped_unavailable_count,
                aggregate.deadline_violation_count,
                aggregate.illegal_action_rejection_count,
                aggregate.mean_delay,
                aggregate.mean_reward,
            )
            for aggregate in self.report.policy_aggregate_metrics
        }
        self.assertGreater(len(aggregate_signatures), 1)

    def test_compatibility_mode_is_not_used_in_default_comparison(self) -> None:
        self.assertTrue(all(not comparison.compatibility_mode_used for comparison in self.comparisons))
        self.assertTrue(all(not aggregate.compatibility_mode_used for aggregate in self.report.policy_aggregate_metrics))
        self.assertFalse(self.report.passed)
        self.assertEqual(self.report.status, "baseline_policy_comparative_evaluation_readiness_with_blockers")
        self.assertFalse(self.report.feature_071_regression_status.passed)
        self.assertIn("compatibility mode", self.report.paper_claim_boundary.lower())


if __name__ == "__main__":
    unittest.main()
