from __future__ import annotations

import unittest

from src.environment.offloading_queue import OffloadingQueue
from src.environment.private_queue import PrivateQueue
from src.environment.public_queue import PublicQueue
from src.environment.task import Task


class QueueWaitingTimeTests(unittest.TestCase):
    def test_private_queue_waiting_time_uses_head_entry_slot(self) -> None:
        queue = PrivateQueue(owner_node_id="ea1")
        first = Task(1, 1, 0, 10, 1, 3, 3)
        second = Task(2, 1, 0, 10, 1, 3, 3)
        queue.enqueue(first, slot=2)
        queue.enqueue(second, slot=4)

        queue.dequeue()

        self.assertEqual(queue.current_head_entered_at, 4)
        self.assertEqual(queue.waiting_time(current_slot=6), 2)

    def test_offloading_queue_waiting_time_uses_head_entry_slot(self) -> None:
        queue = OffloadingQueue(owner_node_id="ea1", resolved_destination="ea2")
        first = Task(1, 1, 0, 10, 1, 3, 3)
        second = Task(2, 1, 0, 10, 1, 3, 3)
        queue.enqueue(first, slot=4)
        queue.enqueue(second, slot=5)

        queue.dequeue()

        self.assertEqual(queue.current_head_entered_at, 5)
        self.assertEqual(queue.waiting_time(current_slot=8), 3)

    def test_public_queue_waiting_time_uses_head_entry_slot(self) -> None:
        queue = PublicQueue(host_node_id="ea2", source_agent_id="ea1")
        first = Task(1, 1, 0, 10, 1, 3, 3)
        second = Task(2, 1, 0, 10, 1, 3, 3)
        queue.enqueue(first, slot=1)
        queue.enqueue(second, slot=3)

        queue.dequeue()

        self.assertEqual(queue.current_head_entered_at, 3)
        self.assertEqual(queue.waiting_time(current_slot=6), 3)


if __name__ == "__main__":
    unittest.main()
