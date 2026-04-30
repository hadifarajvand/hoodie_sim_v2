from __future__ import annotations

import unittest

from src.environment.deadline_rules import has_expired
from src.environment.task import Task


class DeadlineExpirationTests(unittest.TestCase):
    def test_task_has_not_expired_at_deadline_slot(self) -> None:
        task = Task(1, 1, 0, 10, 1, 3, 5)

        self.assertFalse(has_expired(task, current_slot=5))

    def test_task_expires_after_deadline_slot(self) -> None:
        task = Task(1, 1, 0, 10, 1, 3, 5)

        self.assertTrue(has_expired(task, current_slot=6))


if __name__ == "__main__":
    unittest.main()

