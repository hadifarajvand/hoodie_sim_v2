from __future__ import annotations

import unittest

from src.environment.reward_timing import emit_delayed_reward
from src.environment.slot_boundaries import emit_reward_if_terminal
from src.environment.task import Task


class DelayedRewardTests(unittest.TestCase):
    def test_delayed_reward_emission_sets_reward_flag(self) -> None:
        task = Task(1, 1, 0, 10, 1, 3, 5)

        emit_delayed_reward(task)

        self.assertTrue(task.reward_emitted)

    def test_reward_emission_occurs_only_after_terminal_outcome(self) -> None:
        task = Task(1, 1, 0, 10, 1, 3, 5)
        task.terminal_outcome = "completed"

        emit_reward_if_terminal(task)

        self.assertTrue(task.reward_emitted)

    def test_reward_is_not_emitted_at_decision_time(self) -> None:
        task = Task(1, 1, 0, 10, 1, 3, 5)

        emit_reward_if_terminal(task)

        self.assertFalse(task.reward_emitted)


if __name__ == "__main__":
    unittest.main()
