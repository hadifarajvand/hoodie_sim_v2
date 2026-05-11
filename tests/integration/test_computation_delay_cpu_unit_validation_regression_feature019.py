from __future__ import annotations

import unittest

from src.environment.runtime_model import SharedRuntimeParameters, resolve_runtime_terminal_state
from src.environment.task import Task


class Feature019RegressionTests(unittest.TestCase):
    def test_timeout_drop_behavior_remains_intact(self) -> None:
        task = Task(
            task_id=19,
            source_agent_id=1,
            arrival_slot=0,
            size=8.0,
            processing_density=0.297,
            timeout_length=2,
            absolute_deadline_slot=2,
        )
        resolve_runtime_terminal_state(task, terminal_slot=5, current_slot=1, parameters=SharedRuntimeParameters(timeout_grace_slots=0))
        self.assertEqual(task.terminal_outcome, "dropped")
        self.assertTrue(task.drop_flag)
        self.assertTrue(task.reward_emitted)


if __name__ == "__main__":
    unittest.main()
