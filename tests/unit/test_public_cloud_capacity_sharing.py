from __future__ import annotations

import unittest

from src.environment.compute_config import ComputeConfig
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.public_queue import PublicQueue
from src.environment.task import Task


class PublicCloudCapacitySharingUnitTests(unittest.TestCase):
    def _task(self, task_id: int, *, source_agent_id: int, size: float = 1.0, cycles_remaining: float = 1.0) -> Task:
        task = Task(
            task_id=task_id,
            source_agent_id=source_agent_id,
            arrival_slot=0,
            size=size,
            processing_density=1.0,
            timeout_length=20,
            absolute_deadline_slot=20,
            cycles_required=cycles_remaining,
            cycles_remaining=cycles_remaining,
        )
        task.queue_state = "public_queue"
        return task

    def _environment(self) -> HoodieGymEnvironment:
        return HoodieGymEnvironment(episode_length=10, compute_config=ComputeConfig())

    def test_single_public_queue_gets_full_edge_capacity(self) -> None:
        env = self._environment()
        env.current_slot = 1
        queue = PublicQueue(host_node_id="2", source_agent_id="1")
        task = self._task(1, source_agent_id=1, cycles_remaining=0.2)
        queue.enqueue(task, slot=0)
        env._public_queues[("2", "1")] = queue

        finalized = env._progress_execution_queues()

        self.assertEqual(finalized[0].metadata["capacity_sharing_allocated_capacity"], env.compute_config.cpu_capacity_per_slot_edge)
        self.assertEqual(finalized[0].metadata["capacity_sharing_capacity_pool"], env.compute_config.cpu_capacity_per_slot_edge)
        self.assertEqual(finalized[0].metadata["capacity_sharing_active_heads"], 1)
        self.assertEqual(finalized[0].metadata["capacity_sharing_host"], "2")

    def test_two_public_queues_same_host_share_edge_capacity_equally(self) -> None:
        env = self._environment()
        env.current_slot = 1
        queue_a = PublicQueue(host_node_id="2", source_agent_id="1")
        queue_b = PublicQueue(host_node_id="2", source_agent_id="3")
        task_a = self._task(1, source_agent_id=1, cycles_remaining=0.2)
        task_b = self._task(2, source_agent_id=3, cycles_remaining=0.2)
        queue_a.enqueue(task_a, slot=0)
        queue_b.enqueue(task_b, slot=0)
        env._public_queues[("2", "1")] = queue_a
        env._public_queues[("2", "3")] = queue_b

        finalized = env._progress_execution_queues()

        self.assertEqual(len(finalized), 2)
        self.assertEqual(finalized[0].metadata["capacity_sharing_allocated_capacity"], env.compute_config.cpu_capacity_per_slot_edge / 2.0)
        self.assertEqual(finalized[1].metadata["capacity_sharing_allocated_capacity"], env.compute_config.cpu_capacity_per_slot_edge / 2.0)

    def test_two_public_queues_different_hosts_do_not_share_capacity(self) -> None:
        env = self._environment()
        env.current_slot = 1
        queue_a = PublicQueue(host_node_id="2", source_agent_id="1")
        queue_b = PublicQueue(host_node_id="3", source_agent_id="3")
        queue_a.enqueue(self._task(1, source_agent_id=1, cycles_remaining=0.2), slot=0)
        queue_b.enqueue(self._task(2, source_agent_id=3, cycles_remaining=0.2), slot=0)
        env._public_queues[("2", "1")] = queue_a
        env._public_queues[("3", "3")] = queue_b

        finalized = env._progress_execution_queues()

        self.assertEqual(finalized[0].metadata["capacity_sharing_allocated_capacity"], env.compute_config.cpu_capacity_per_slot_edge)
        self.assertEqual(finalized[1].metadata["capacity_sharing_allocated_capacity"], env.compute_config.cpu_capacity_per_slot_edge)

    def test_two_cloud_queues_share_global_cloud_capacity_equally(self) -> None:
        env = self._environment()
        env.current_slot = 1
        queue_a = PublicQueue(host_node_id="cloud", source_agent_id="1")
        queue_b = PublicQueue(host_node_id="cloud", source_agent_id="3")
        queue_a.enqueue(self._task(1, source_agent_id=1, cycles_remaining=0.2), slot=0)
        queue_b.enqueue(self._task(2, source_agent_id=3, cycles_remaining=0.2), slot=0)
        env._public_queues[("cloud", "1")] = queue_a
        env._public_queues[("cloud", "3")] = queue_b

        finalized = env._progress_execution_queues()

        expected = env.compute_config.cpu_capacity_per_slot_cloud / 2.0
        self.assertEqual(finalized[0].metadata["capacity_sharing_allocated_capacity"], expected)
        self.assertEqual(finalized[1].metadata["capacity_sharing_allocated_capacity"], expected)

    def test_total_public_host_consumption_does_not_exceed_edge_capacity(self) -> None:
        env = self._environment()
        env.current_slot = 1
        queue_a = PublicQueue(host_node_id="2", source_agent_id="1")
        queue_b = PublicQueue(host_node_id="2", source_agent_id="3")
        queue_a.enqueue(self._task(1, source_agent_id=1, cycles_remaining=0.2), slot=0)
        queue_b.enqueue(self._task(2, source_agent_id=3, cycles_remaining=0.2), slot=0)
        env._public_queues[("2", "1")] = queue_a
        env._public_queues[("2", "3")] = queue_b

        finalized = env._progress_execution_queues()

        total = finalized[0].metadata["execution_cycles_consumed"] + finalized[1].metadata["execution_cycles_consumed"]
        self.assertLessEqual(total, env.compute_config.cpu_capacity_per_slot_edge)

    def test_total_cloud_consumption_does_not_exceed_cloud_capacity(self) -> None:
        env = self._environment()
        env.current_slot = 1
        queue_a = PublicQueue(host_node_id="cloud", source_agent_id="1")
        queue_b = PublicQueue(host_node_id="cloud", source_agent_id="3")
        queue_a.enqueue(self._task(1, source_agent_id=1, cycles_remaining=0.2), slot=0)
        queue_b.enqueue(self._task(2, source_agent_id=3, cycles_remaining=0.2), slot=0)
        env._public_queues[("cloud", "1")] = queue_a
        env._public_queues[("cloud", "3")] = queue_b

        finalized = env._progress_execution_queues()

        total = finalized[0].metadata["execution_cycles_consumed"] + finalized[1].metadata["execution_cycles_consumed"]
        self.assertLessEqual(total, env.compute_config.cpu_capacity_per_slot_cloud)

    def test_capacity_sharing_order_is_deterministic(self) -> None:
        def build_finalized_task_ids() -> list[int]:
            env = self._environment()
            env.current_slot = 1
            queue_a = PublicQueue(host_node_id="2", source_agent_id="3")
            queue_b = PublicQueue(host_node_id="2", source_agent_id="1")
            queue_c = PublicQueue(host_node_id="cloud", source_agent_id="2")
            queue_a.enqueue(self._task(3, source_agent_id=3, cycles_remaining=0.2), slot=0)
            queue_b.enqueue(self._task(1, source_agent_id=1, cycles_remaining=0.2), slot=0)
            queue_c.enqueue(self._task(2, source_agent_id=2, cycles_remaining=0.2), slot=0)
            env._public_queues[("2", "3")] = queue_a
            env._public_queues[("2", "1")] = queue_b
            env._public_queues[("cloud", "2")] = queue_c
            finalized = env._progress_execution_queues()
            return [task.task_id for task in finalized]

        first = build_finalized_task_ids()
        second = build_finalized_task_ids()

        self.assertEqual(first, second)
        self.assertEqual(first, [1, 3, 2])


if __name__ == "__main__":
    unittest.main()
