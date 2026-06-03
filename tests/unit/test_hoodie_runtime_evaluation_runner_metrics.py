from __future__ import annotations

import unittest

from src.analysis.hoodie_runtime_evaluation_runner.metrics import build_metric_row, completion_rate, queue_stability_score, task_completion_delay, task_drop_ratio, throughput
from src.analysis.hoodie_runtime_evaluation_runner.model import ExecutionOutcome


class HoodieRuntimeEvaluationRunnerMetricsTests(unittest.TestCase):
    def test_metric_helpers_handle_basic_values(self) -> None:
        self.assertEqual(completion_rate(3, 4), 0.75)
        self.assertEqual(throughput(6, 12), 0.5)
        self.assertEqual(task_completion_delay([1.0, 3.0]), 2.0)
        self.assertEqual(task_drop_ratio(2, 1, 6), 0.5)
        self.assertGreater(queue_stability_score([(1, 1, 1), (1, 2, 2)]), 0.0)

    def test_build_metric_row_aggregates_outcomes(self) -> None:
        outcomes = (
            ExecutionOutcome("t1", True, False, False, False, False, 0, 2, 2.0, -2.0, (1, 1, 1), "POLICY", "scenario", "low", "tight", 7, "local", "self", False, ("policy=POLICY",), "policy=POLICY"),
            ExecutionOutcome("t2", False, True, False, False, True, 1, None, None, -40.0, (2, 2, 2), "POLICY", "scenario", "low", "tight", 7, "horizontal", "illegal", True, ("policy=POLICY",), "policy=POLICY"),
        )
        row = build_metric_row(policy="POLICY", scenario="scenario", workload="low", deadline_pressure="tight", seed=7, outcomes=outcomes)
        self.assertEqual(row.completed_count, 1)
        self.assertEqual(row.dropped_timeout_count, 1)
        self.assertEqual(row.dropped_unavailable_count, 0)
        self.assertEqual(row.illegal_action_rejection_count, 1)
        self.assertAlmostEqual(row.completion_rate, 0.5)
        self.assertAlmostEqual(row.timeout_drop_rate, 0.5)
        self.assertAlmostEqual(row.total_reward, -42.0)
        self.assertAlmostEqual(row.task_completion_delay, 2.0)
        self.assertAlmostEqual(row.task_drop_ratio, 0.5)


if __name__ == "__main__":
    unittest.main()
