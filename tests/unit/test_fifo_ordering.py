from __future__ import annotations

import unittest

from src.environment.offloading_queue import OffloadingQueue
from src.environment.private_queue import PrivateQueue
from src.environment.public_queue import PublicQueue
from src.environment.task import Task


class FIFOOrderingTests(unittest.TestCase):
    def test_private_queue_preserves_fifo_order(self) -> None:
        queue = PrivateQueue(owner_node_id="ea1")
        first = Task(1, 1, 0, 10, 1, 3, 3)
        second = Task(2, 1, 0, 10, 1, 3, 3)

        queue.enqueue(first, slot=0)
        queue.enqueue(second, slot=0)

        self.assertIs(queue.dequeue(), first)
        self.assertIs(queue.dequeue(), second)

    def test_offloading_queue_preserves_fifo_order(self) -> None:
        queue = OffloadingQueue(owner_node_id="ea1", resolved_destination="ea2")
        first = Task(1, 1, 0, 10, 1, 3, 3)
        second = Task(2, 1, 0, 10, 1, 3, 3)

        queue.enqueue(first, slot=1)
        queue.enqueue(second, slot=2)

        self.assertIs(queue.dequeue(), first)
        self.assertIs(queue.dequeue(), second)

    def test_public_queue_preserves_fifo_order(self) -> None:
        queue = PublicQueue(host_node_id="ea2", source_agent_id="ea1")
        first = Task(1, 1, 0, 10, 1, 3, 3)
        second = Task(2, 1, 0, 10, 1, 3, 3)

        queue.enqueue(first, slot=1)
        queue.enqueue(second, slot=2)

        self.assertIs(queue.dequeue(), first)
        self.assertIs(queue.dequeue(), second)


if __name__ == "__main__":
    unittest.main()

