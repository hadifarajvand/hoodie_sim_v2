from __future__ import annotations

import unittest

from src.environment.compute_config import ComputeConfig
from src.environment.execution_helper import step_execution
from src.environment.task import Task


class ExecutionHelperTests(unittest.TestCase):
    def _task(self, *, task_id: int, cycles_required: float, timeout_length: int = 20) -> Task:
        return Task(
            task_id=task_id,
            source_agent_id=1,
            arrival_slot=0,
            size=cycles_required,
            processing_density=1.0,
            timeout_length=timeout_length,
            absolute_deadline_slot=timeout_length,
            cycles_required=cycles_required,
            cycles_remaining=cycles_required,
        )

    def test_local_execution_no_single_slot_shortcut_when_cycles_exceed_capacity(self) -> None:
        task = self._task(task_id=1, cycles_required=1.0)

        progress = step_execution(task, 0.5, slot=0, destination_kind="local")

        self.assertFalse(progress.completed)
        self.assertEqual(progress.cycles_consumed, 0.5)
        self.assertEqual(progress.cycles_after, 0.5)
        self.assertIsNone(task.completion_slot)

    def test_local_execution_consumes_at_most_agent_capacity_per_slot(self) -> None:
        task = self._task(task_id=2, cycles_required=1.0)

        progress = step_execution(task, ComputeConfig().cpu_capacity_per_slot_agent, slot=0, destination_kind="local")

        self.assertLessEqual(progress.cycles_consumed, 0.5)
        self.assertEqual(progress.cycles_after, 0.5)

    def test_public_execution_consumes_at_most_edge_capacity_per_slot(self) -> None:
        task = self._task(task_id=3, cycles_required=1.0)

        progress = step_execution(task, ComputeConfig().cpu_capacity_per_slot_edge, slot=0, destination_kind="public")

        self.assertLessEqual(progress.cycles_consumed, 0.5)
        self.assertEqual(progress.cycles_after, 0.5)

    def test_cloud_execution_consumes_at_most_cloud_capacity_per_slot(self) -> None:
        task = self._task(task_id=4, cycles_required=5.0)

        progress = step_execution(task, ComputeConfig().cpu_capacity_per_slot_cloud, slot=0, destination_kind="cloud")

        self.assertLessEqual(progress.cycles_consumed, 3.0)
        self.assertEqual(progress.cycles_after, 2.0)

    def test_execution_exact_capacity_boundary_completion_contract(self) -> None:
        task = self._task(task_id=5, cycles_required=0.5)

        progress = step_execution(task, 0.5, slot=7, destination_kind="local")

        self.assertTrue(progress.completed)
        self.assertEqual(progress.cycles_after, 0.0)
        self.assertEqual(task.completion_slot, 7)

    def test_cycles_remaining_decreases_monotonically(self) -> None:
        task = self._task(task_id=6, cycles_required=2.0)

        first = step_execution(task, 0.5, slot=0, destination_kind="local")
        second = step_execution(task, 0.5, slot=1, destination_kind="local")
        third = step_execution(task, 0.5, slot=2, destination_kind="local")

        self.assertGreater(first.cycles_before, first.cycles_after)
        self.assertGreater(second.cycles_before, second.cycles_after)
        self.assertGreater(third.cycles_before, third.cycles_after)
        self.assertGreaterEqual(first.cycles_after, second.cycles_after)
        self.assertGreaterEqual(second.cycles_after, third.cycles_after)


if __name__ == "__main__":
    unittest.main()
