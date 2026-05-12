from __future__ import annotations

import unittest

from src.environment.compute_config import ComputeConfig
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.public_queue import PublicQueue
from src.environment.private_queue import PrivateQueue
from src.environment.task import Task


class PublicCloudCapacitySharingFlowIntegrationTests(unittest.TestCase):
    def _task(self, task_id: int, *, source_agent_id: int, cycles_remaining: float) -> Task:
        task = Task(
            task_id=task_id,
            source_agent_id=source_agent_id,
            arrival_slot=0,
            size=1.0,
            processing_density=1.0,
            timeout_length=20,
            absolute_deadline_slot=20,
            cycles_required=cycles_remaining,
            cycles_remaining=cycles_remaining,
        )
        task.queue_state = "public_queue"
        return task

    def test_local_private_execution_not_changed(self) -> None:
        env = HoodieGymEnvironment(episode_length=10, compute_config=ComputeConfig())
        queue = PrivateQueue(owner_node_id="1")
        task = Task(
            task_id=1,
            source_agent_id=1,
            arrival_slot=0,
            size=1.0,
            processing_density=1.0,
            timeout_length=20,
            absolute_deadline_slot=20,
            cycles_required=0.25,
            cycles_remaining=0.25,
        )
        queue.enqueue(task, slot=0)
        env._private_queues["1"] = queue

        finalized = env._progress_execution_queues()

        self.assertEqual(len(finalized), 1)
        self.assertEqual(finalized[0].queue_state, "private_queue")
        self.assertNotIn("capacity_sharing_host", finalized[0].metadata)

    def test_feature_033_execution_contract_not_changed(self) -> None:
        from src.environment.execution_helper import step_execution

        task = self._task(1, source_agent_id=1, cycles_remaining=0.5)
        progress = step_execution(task, 0.25, slot=0, destination_kind="public")

        self.assertEqual(progress.destination_kind, "public")
        self.assertEqual(progress.cycles_consumed, 0.25)
        self.assertEqual(task.metadata["execution_cycles_consumed"], 0.25)

    def test_feature_034_transmission_delay_contract_not_changed(self) -> None:
        from src.environment.link_rate_config import compute_transmission_delay, mbits_to_bits

        payload_bits = mbits_to_bits(3.0)
        horizontal = compute_transmission_delay(payload_bits, 30_000_000.0, slot_duration_seconds=0.1, rounding_policy="ceil")
        vertical = compute_transmission_delay(payload_bits, 10_000_000.0, slot_duration_seconds=0.1, rounding_policy="ceil")
        self.assertGreater(vertical.delay_slots, horizontal.delay_slots)

    def test_reward_timing_not_changed(self) -> None:
        env = HoodieGymEnvironment(episode_length=10, compute_config=ComputeConfig())
        queue = PublicQueue(host_node_id="2", source_agent_id="1")
        queue.enqueue(self._task(1, source_agent_id=1, cycles_remaining=0.1), slot=0)
        env._public_queues[("2", "1")] = queue

        finalized = env._progress_execution_queues()

        self.assertTrue(finalized)
        self.assertTrue(finalized[0].completion_slot is not None)
        self.assertNotIn("reward_emitted", finalized[0].metadata)

    def test_scope_guard_no_training_policy_dependency_campaign_drift(self) -> None:
        env = HoodieGymEnvironment(episode_length=10, compute_config=ComputeConfig())
        self.assertEqual(env.compute_config.cpu_capacity_per_slot_edge, 0.5)
        self.assertEqual(env.compute_config.cpu_capacity_per_slot_cloud, 3.0)

    def test_two_public_queues_same_host_share_edge_capacity_equally(self) -> None:
        env = HoodieGymEnvironment(episode_length=10, compute_config=ComputeConfig())
        queue_a = PublicQueue(host_node_id="2", source_agent_id="1")
        queue_b = PublicQueue(host_node_id="2", source_agent_id="2")
        queue_a.enqueue(self._task(1, source_agent_id=1, cycles_remaining=0.2), slot=0)
        queue_b.enqueue(self._task(2, source_agent_id=2, cycles_remaining=0.2), slot=0)
        env._public_queues[("2", "1")] = queue_a
        env._public_queues[("2", "2")] = queue_b

        finalized = env._progress_execution_queues()

        expected = env.compute_config.cpu_capacity_per_slot_edge / 2.0
        self.assertEqual(finalized[0].metadata["capacity_sharing_allocated_capacity"], expected)
        self.assertEqual(finalized[1].metadata["capacity_sharing_allocated_capacity"], expected)


if __name__ == "__main__":
    unittest.main()
