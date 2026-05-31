from __future__ import annotations

import unittest

from src.analysis.controlled_evaluation_batch_readiness import report as batch_report
from src.analysis.controlled_evaluation_batch_readiness.report import (
    build_controlled_evaluation_scenarios,
    compute_aggregate_metrics,
    compute_scenario_metrics,
)


class ControlledEvaluationBatchReadinessMetricsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenarios = build_controlled_evaluation_scenarios()

    def test_per_scenario_metrics_are_computed_deterministically(self) -> None:
        light_load = next(item for item in self.scenarios if item.scenario_id == "light_load_no_deadline_pressure")
        metrics = compute_scenario_metrics(light_load.tasks)
        self.assertEqual(metrics.completed_count, 1)
        self.assertEqual(metrics.dropped_timeout_count, 0)
        self.assertEqual(metrics.dropped_unavailable_count, 0)
        self.assertEqual(metrics.deadline_violation_count, 0)
        self.assertEqual(metrics.illegal_action_rejection_count, 0)
        self.assertEqual(metrics.average_delay, 3.0)
        self.assertEqual(metrics.average_reward, -3.0)
        self.assertEqual(metrics.paper_mode_success_count, 1)
        self.assertFalse(metrics.compatibility_mode_used)

    def test_local_reward_and_delay_change_with_completion_slot(self) -> None:
        early = batch_report._local_task_record(task_id="local-1", arrival_slot=2, phi=4, completion_slot=4)
        late = batch_report._local_task_record(task_id="local-2", arrival_slot=2, phi=5, completion_slot=5)
        self.assertEqual(early.terminal_status, "completed_private")
        self.assertEqual(late.terminal_status, "completed_private")
        self.assertEqual(early.delay, 3)
        self.assertEqual(late.delay, 4)
        self.assertEqual(early.reward_value, -3.0)
        self.assertEqual(late.reward_value, -4.0)

    def test_timeout_and_illegal_counts(self) -> None:
        illegal = next(item for item in self.scenarios if item.scenario_id == "illegal_horizontal_destination_attempt")
        timeout = next(item for item in self.scenarios if item.scenario_id == "timeout_drop_case")
        illegal_metrics = compute_scenario_metrics(illegal.tasks)
        timeout_metrics = compute_scenario_metrics(timeout.tasks)
        self.assertEqual(illegal_metrics.dropped_unavailable_count, 1)
        self.assertEqual(illegal_metrics.illegal_action_rejection_count, 1)
        self.assertEqual(timeout_metrics.dropped_timeout_count, 1)
        self.assertEqual(timeout_metrics.deadline_violation_count, 1)

    def test_late_cloud_completion_drops_instead_of_completing(self) -> None:
        cloud_task = batch_report._cloud_task_record(task_id="cloud-late", arrival_slot=2, phi=4, completion_slot=6)
        self.assertEqual(cloud_task.terminal_status, "dropped_timeout")
        self.assertTrue(cloud_task.deadline_violation)
        self.assertEqual(cloud_task.reward_value, -40.0)
        self.assertEqual(cloud_task.terminal_status, "dropped_timeout")

    def test_aggregate_metrics_are_computed_from_scenarios(self) -> None:
        aggregate = compute_aggregate_metrics(self.scenarios)
        self.assertEqual(aggregate.completed_count, 6)
        self.assertEqual(aggregate.dropped_timeout_count, 2)
        self.assertEqual(aggregate.dropped_unavailable_count, 1)
        self.assertEqual(aggregate.deadline_violation_count, 2)
        self.assertEqual(aggregate.illegal_action_rejection_count, 1)
        self.assertAlmostEqual(aggregate.average_delay, 32.0 / 9.0)
        self.assertAlmostEqual(aggregate.average_reward, -142.0 / 9.0)
        self.assertEqual(aggregate.paper_mode_success_count, 6)
        self.assertFalse(aggregate.compatibility_mode_used)
