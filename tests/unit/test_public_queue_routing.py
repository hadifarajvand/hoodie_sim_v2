from __future__ import annotations

import unittest

from src.environment.public_queue import PublicQueue
from src.environment.task import Task


class PublicQueueRoutingTests(unittest.TestCase):
    def test_public_queue_identity_uses_host_and_source_pair(self) -> None:
        queue = PublicQueue(host_node_id="ea2", source_agent_id="ea1")

        self.assertEqual(queue.identity, ("ea2", "ea1"))

    def test_public_queue_routes_tasks_by_host_and_source_pair(self) -> None:
        queue = PublicQueue(host_node_id="ea2", source_agent_id="ea1")
        task = Task(1, 1, 0, 10, 1, 3, 3)

        queue.enqueue(task, slot=1)

        self.assertEqual(task.queue_state, "public_queue")
        self.assertEqual(task.metadata["queue_entered_at"], 1)
        self.assertEqual(queue.dequeue(), task)

    def test_public_queues_on_same_host_remain_separated_by_source(self) -> None:
        queue_from_ea1 = PublicQueue(host_node_id="ea2", source_agent_id="ea1")
        queue_from_ea3 = PublicQueue(host_node_id="ea2", source_agent_id="ea3")
        task_from_ea1 = Task(1, 1, 0, 10, 1, 3, 3)
        task_from_ea3 = Task(2, 3, 0, 10, 1, 3, 3)

        queue_from_ea1.enqueue(task_from_ea1, slot=1)
        queue_from_ea3.enqueue(task_from_ea3, slot=2)

        self.assertEqual(queue_from_ea1.identity, ("ea2", "ea1"))
        self.assertEqual(queue_from_ea3.identity, ("ea2", "ea3"))
        self.assertEqual(queue_from_ea1.dequeue(), task_from_ea1)
        self.assertEqual(queue_from_ea3.dequeue(), task_from_ea3)
        self.assertEqual(task_from_ea1.metadata["queue_entered_at"], 1)
        self.assertEqual(task_from_ea3.metadata["queue_entered_at"], 2)

    def test_public_queue_admission_after_offload_retains_offload_identity(self) -> None:
        queue = PublicQueue(host_node_id="cloud", source_agent_id="ea1")
        task = Task(3, 1, 0, 12, 2, 4, 4)

        queue.enqueue(task, slot=5)

        self.assertEqual(task.queue_state, "public_queue")
        self.assertEqual(task.metadata["queue_entered_at"], 5)
        self.assertEqual(queue.identity, ("cloud", "ea1"))
        self.assertEqual(queue.dequeue(), task)


if __name__ == "__main__":
    unittest.main()
