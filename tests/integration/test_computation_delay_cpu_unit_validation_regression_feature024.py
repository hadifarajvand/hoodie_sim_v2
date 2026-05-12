from __future__ import annotations

import unittest

from src.environment.execution_helper import step_execution
from src.environment.task import Task


class Feature024RegressionTests(unittest.TestCase):
    def test_local_compute_and_deterministic_ordering_remain_intact(self) -> None:
        task = Task(
            task_id=24,
            source_agent_id=1,
            arrival_slot=0,
            size=10.0,
            processing_density=1.0,
            timeout_length=1,
            absolute_deadline_slot=20,
        )
        first = step_execution(task, 6.0, slot=0, destination_kind="local")
        second = step_execution(task, 6.0, slot=1, destination_kind="local")
        self.assertLess(second.cycles_after, first.cycles_after)
        self.assertEqual(first.cycles_after, 4.0)
        self.assertEqual(second.cycles_after, 0.0)
        self.assertEqual(task.completion_slot, 1)


if __name__ == "__main__":
    unittest.main()
