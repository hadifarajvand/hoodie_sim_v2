from __future__ import annotations

import unittest

from src.environment.slot_boundaries import resolve_terminal_state
from src.environment.task import Task


class CompletionDropPrecedenceTests(unittest.TestCase):
    def test_completion_wins_when_task_finishes_on_or_before_deadline(self) -> None:
        task = Task(1, 1, 0, 10, 1, 3, 5, completion_slot=5)

        outcome = resolve_terminal_state(task, current_slot=5)

        self.assertEqual(outcome, "completed")
        self.assertEqual(task.terminal_outcome, "completed")
        self.assertFalse(task.drop_flag)

    def test_drop_wins_when_task_is_over_deadline_without_completion(self) -> None:
        task = Task(1, 1, 0, 10, 1, 3, 5)

        outcome = resolve_terminal_state(task, current_slot=6)

        self.assertEqual(outcome, "dropped")
        self.assertEqual(task.terminal_outcome, "dropped")
        self.assertTrue(task.drop_flag)


if __name__ == "__main__":
    unittest.main()

