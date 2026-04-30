from __future__ import annotations

import unittest

from src.environment.task import Task


class TaskLifecycleTests(unittest.TestCase):
    def test_task_defaults_capture_terminal_state_fields(self) -> None:
        task = Task(
            task_id=1,
            source_agent_id=2,
            arrival_slot=3,
            size=100,
            processing_density=4,
            timeout_length=5,
            absolute_deadline_slot=8,
        )

        self.assertIsNone(task.selected_action)
        self.assertIsNone(task.resolved_destination)
        self.assertEqual(task.queue_state, "created")
        self.assertIsNone(task.start_slot)
        self.assertIsNone(task.completion_slot)
        self.assertIsNone(task.terminal_outcome)
        self.assertFalse(task.reward_emitted)
        self.assertFalse(task.drop_flag)

    def test_task_supports_explicit_lifecycle_updates_without_extra_logic(self) -> None:
        task = Task(
            task_id=7,
            source_agent_id=11,
            arrival_slot=1,
            size=256,
            processing_density=9,
            timeout_length=4,
            absolute_deadline_slot=5,
        )

        task.selected_action = "local"
        task.resolved_destination = "self"
        task.queue_state = "queued"
        task.start_slot = 2
        task.completion_slot = 4
        task.terminal_outcome = "completed"
        task.reward_emitted = True

        self.assertEqual(task.selected_action, "local")
        self.assertEqual(task.resolved_destination, "self")
        self.assertEqual(task.queue_state, "queued")
        self.assertEqual(task.start_slot, 2)
        self.assertEqual(task.completion_slot, 4)
        self.assertEqual(task.terminal_outcome, "completed")
        self.assertTrue(task.reward_emitted)

    def test_task_construction_preserves_basic_time_order_invariants(self) -> None:
        task = Task(
            task_id=9,
            source_agent_id=4,
            arrival_slot=2,
            size=128,
            processing_density=3,
            timeout_length=6,
            absolute_deadline_slot=8,
        )

        self.assertGreaterEqual(task.absolute_deadline_slot, task.arrival_slot)
        self.assertGreater(task.timeout_length, 0)


if __name__ == "__main__":
    unittest.main()
