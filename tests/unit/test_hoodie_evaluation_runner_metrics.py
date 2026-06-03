from __future__ import annotations

import unittest

from src.analysis.hoodie_evaluation_runner.metrics import (
    average_delay,
    average_reward,
    build_metric_row,
    completion_rate,
    deadline_violation_rate,
    queue_stability_score,
    timeout_drop_rate,
    total_reward,
    throughput,
    unavailable_drop_rate,
)
from src.analysis.hoodie_evaluation_runner.model import ExecutionOutcome


class HoodieEvaluationRunnerMetricsTests(unittest.TestCase):
    def test_scalar_metric_formulas_are_deterministic(self) -> None:
        self.assertEqual(completion_rate(3, 5), 0.6)
        self.assertEqual(timeout_drop_rate(1, 5), 0.2)
        self.assertEqual(unavailable_drop_rate(1, 5), 0.2)
        self.assertEqual(deadline_violation_rate(2, 5), 0.4)
        self.assertEqual(average_delay([1.0, 3.0, None]), 2.0)
        self.assertEqual(average_reward([-1.0, -3.0]), -2.0)
        self.assertEqual(total_reward([-1.0, -3.0, None]), -4.0)
        self.assertEqual(throughput(3, 6), 0.5)
        self.assertGreater(queue_stability_score(((0, 1, 2), (1, 1, 2), (1, 2, 3))), 0.0)

    def test_metric_row_builds_from_execution_outcomes(self) -> None:
        outcomes = (
            ExecutionOutcome(
                task_id="t1",
                completed=True,
                dropped_timeout=False,
                dropped_unavailable=False,
                deadline_violation=False,
                illegal_action_rejected=False,
                arrival_time=0,
                completion_time=2,
                delay=2.0,
                reward=-2.0,
                queue_length_observations=(0, 1, 1),
                policy="LOCAL_ONLY",
                scenario_name="light_load_no_deadline_pressure",
                workload="low",
                deadline_pressure="relaxed",
                seed=7,
                selected_action="local",
                resolved_destination="self",
                compatibility_mode_used=False,
            ),
            ExecutionOutcome(
                task_id="t2",
                completed=False,
                dropped_timeout=True,
                dropped_unavailable=False,
                deadline_violation=False,
                illegal_action_rejected=False,
                arrival_time=1,
                completion_time=None,
                delay=None,
                reward=-40.0,
                queue_length_observations=(1, 2, 2),
                policy="LOCAL_ONLY",
                scenario_name="light_load_no_deadline_pressure",
                workload="low",
                deadline_pressure="relaxed",
                seed=7,
                selected_action="local",
                resolved_destination="self",
                compatibility_mode_used=False,
            ),
        )
        row = build_metric_row(
            policy="LOCAL_ONLY",
            scenario="light_load_no_deadline_pressure",
            workload="low",
            deadline_pressure="relaxed",
            seed=7,
            outcomes=outcomes,
            scenario_duration=4,
        )
        self.assertEqual(row.completed_count, 1)
        self.assertEqual(row.dropped_timeout_count, 1)
        self.assertEqual(row.completion_rate, 0.5)
        self.assertEqual(row.total_reward, -42.0)
        self.assertAlmostEqual(row.average_delay, 2.0)


if __name__ == "__main__":
    unittest.main()
