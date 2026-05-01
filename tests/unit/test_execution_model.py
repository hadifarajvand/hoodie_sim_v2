from __future__ import annotations

import unittest

from src.environment.execution_helper import step_execution
from src.environment.task import Task


class ExecutionModelTests(unittest.TestCase):
    def test_compute_budget_matches_paper_formula(self) -> None:
        task = Task(
            task_id=1,
            source_agent_id=1,
            arrival_slot=0,
            size=2.1,
            processing_density=0.297,
            timeout_length=20,
            absolute_deadline_slot=20,
        )

        self.assertAlmostEqual(task.cycles_required, 2.1 * 0.297)
        self.assertAlmostEqual(task.cycles_remaining, 2.1 * 0.297)

    def test_step_execution_decrements_remaining_cycles_deterministically(self) -> None:
        task = Task(
            task_id=2,
            source_agent_id=1,
            arrival_slot=0,
            size=10.0,
            processing_density=1.0,
            timeout_length=20,
            absolute_deadline_slot=20,
        )

        first = step_execution(task, 4.0, slot=0, destination_kind="local")
        second = step_execution(task, 4.0, slot=1, destination_kind="local")
        third = step_execution(task, 4.0, slot=2, destination_kind="local")
        final = step_execution(task, 4.0, slot=3, destination_kind="local")

        self.assertEqual(first.cycles_before, 10.0)
        self.assertEqual(first.cycles_after, 6.0)
        self.assertFalse(first.completed)
        self.assertEqual(second.cycles_after, 2.0)
        self.assertFalse(second.completed)
        self.assertEqual(third.cycles_after, 0.0)
        self.assertFalse(third.completed)
        self.assertEqual(task.completion_slot, 3)
        self.assertTrue(final.completed)
        self.assertEqual(final.cycles_after, 0.0)

    def test_fractional_paper_values_are_preserved_through_execution(self) -> None:
        task = Task(
            task_id=3,
            source_agent_id=2,
            arrival_slot=0,
            size=2.1,
            processing_density=0.297,
            timeout_length=20,
            absolute_deadline_slot=20,
        )

        progress = step_execution(task, 0.5, slot=0, destination_kind="public")

        self.assertAlmostEqual(progress.cycles_before, 2.1 * 0.297)
        self.assertAlmostEqual(progress.cycles_after, max(0.0, 2.1 * 0.297 - 0.5))
        self.assertAlmostEqual(task.cycles_remaining, max(0.0, 2.1 * 0.297 - 0.5))

    def test_non_positive_capacity_is_rejected(self) -> None:
        task = Task(
            task_id=4,
            source_agent_id=1,
            arrival_slot=0,
            size=10.0,
            processing_density=1.0,
            timeout_length=20,
            absolute_deadline_slot=20,
        )

        with self.assertRaises(ValueError):
            step_execution(task, 0.0, slot=0, destination_kind="local")


if __name__ == "__main__":
    unittest.main()
