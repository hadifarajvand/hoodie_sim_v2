from __future__ import annotations

import unittest

from src.environment.deadline_rules import has_expired
from src.environment.task import Task


class DeadlineRulesTests(unittest.TestCase):
    def _task(self, arrival_slot: int = 0, absolute_deadline_slot: int = 20) -> Task:
        return Task(
            task_id=1,
            source_agent_id=1,
            arrival_slot=arrival_slot,
            size=1.0,
            processing_density=1.0,
            timeout_length=absolute_deadline_slot - arrival_slot,
            absolute_deadline_slot=absolute_deadline_slot,
        )

    def test_task_not_expired_before_deadline(self) -> None:
        task = self._task()
        self.assertFalse(has_expired(task, current_slot=19))

    def test_task_not_expired_at_deadline(self) -> None:
        task = self._task()
        self.assertFalse(has_expired(task, current_slot=20))

    def test_task_expires_after_deadline(self) -> None:
        task = self._task()
        self.assertTrue(has_expired(task, current_slot=21))


if __name__ == "__main__":
    unittest.main()

