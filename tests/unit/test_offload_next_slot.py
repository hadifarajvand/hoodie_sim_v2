from __future__ import annotations

import unittest

from src.environment.offloading_queue import OffloadingQueue
from src.environment.public_queue import PublicQueue
from src.environment.slot_engine import SlotEngine
from src.environment.task import Task


class OffloadNextSlotTests(unittest.TestCase):
    def test_offload_completes_into_public_queue_on_next_slot(self) -> None:
        engine = SlotEngine(current_slot=5)
        queue = OffloadingQueue(owner_node_id="ea1", resolved_destination="ea2")
        public_queue = PublicQueue(host_node_id="ea2", source_agent_id="ea1")
        task = Task(1, 1, 0, 10, 1, 3, 3)

        queue.enqueue(task, slot=5)

        admitted_same_slot = engine.admit_offload_completion(queue, public_queue, completion_slot=5)
        self.assertFalse(admitted_same_slot)
        self.assertEqual(len(public_queue.tasks), 0)

        admitted_next_slot = engine.admit_offload_completion(queue, public_queue, completion_slot=6)
        self.assertTrue(admitted_next_slot)
        self.assertEqual(len(public_queue.tasks), 1)
        self.assertIs(public_queue.dequeue(), task)
        self.assertEqual(task.resolved_destination, "ea2")


if __name__ == "__main__":
    unittest.main()
