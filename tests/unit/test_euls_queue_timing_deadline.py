from __future__ import annotations

import unittest

from src.environment.compute_config import ComputeConfig
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.offloading_queue import OffloadingQueue
from src.environment.private_queue import PrivateQueue
from src.environment.public_queue import PublicQueue
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph
from src.environment.task import Task
from src.evaluation.trace_protocol import EvaluationTrace, TraceTaskBlueprint


class EULSQueueTimingDeadlineTests(unittest.TestCase):
    def _env(self, *, topology: TopologyGraph | None = None, compute_config: ComputeConfig | None = None) -> HoodieGymEnvironment:
        return HoodieGymEnvironment(
            episode_length=6,
            topology=topology,
            runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
            compute_config=compute_config or ComputeConfig(cpu_capacity_per_slot_agent=64.0, cpu_capacity_per_slot_edge=64.0, cpu_capacity_per_slot_cloud=64.0),
            policy_name="FLC",
        )

    def _trace(self, *tasks: TraceTaskBlueprint) -> EvaluationTrace:
        return EvaluationTrace(
            trace_id="phase2",
            seed=1,
            tasks=tasks,
            metadata={"mode": "deterministic_seed", "trace_id": "phase2", "seed": "1"},
        )

    def test_private_queue_fifo_and_no_same_slot_second_head_service(self) -> None:
        env = self._env()
        trace = self._trace(
            TraceTaskBlueprint(task_id=1, source_agent_id=1, arrival_slot=0, size=32.0, processing_density=1.0, timeout_length=5, absolute_deadline_slot=5),
            TraceTaskBlueprint(task_id=2, source_agent_id=1, arrival_slot=0, size=32.0, processing_density=1.0, timeout_length=5, absolute_deadline_slot=5),
        )
        env.trace = trace
        env._pending_arrivals = {0: [trace.tasks[0], trace.tasks[1]]}  # type: ignore[assignment]
        env.current_slot = 0
        env._current_task = env._load_current_task()

        _obs0, _reward0, _terminated0, _truncated0, info0 = env.step("local")
        self.assertEqual(info0["queue_load"], 0)
        self.assertEqual(env.current_task.task_id, 2)
        self.assertFalse(_terminated0)
        self.assertFalse(_truncated0)

        _obs1, _reward1, _terminated1, _truncated1, info1 = env.step("local")
        self.assertEqual(info1["queue_load"], 0)
        self.assertEqual(info1["finalized_tasks"][0]["task_id"], 1)
        self.assertEqual(env._history[0].task_id, 1)
        self.assertFalse(_truncated1)

    def test_offloading_queue_fifo(self) -> None:
        env = self._env(topology=TopologyGraph(node_ids=("1", "2"), legal_adjacency={"1": ("2",)}), compute_config=ComputeConfig(cpu_capacity_per_slot_agent=64.0, cpu_capacity_per_slot_edge=1.0, cpu_capacity_per_slot_cloud=1.0))
        first = Task(task_id=1, source_agent_id=1, arrival_slot=0, size=2.0, processing_density=1.0, timeout_length=5, absolute_deadline_slot=5)
        second = Task(task_id=2, source_agent_id=1, arrival_slot=0, size=2.0, processing_density=1.0, timeout_length=5, absolute_deadline_slot=5)
        first.metadata["transmission_started_at"] = 0
        first.metadata["transmission_delay_slots"] = 1
        second.metadata["transmission_started_at"] = 0
        second.metadata["transmission_delay_slots"] = 1
        queue = OffloadingQueue(owner_node_id="1", resolved_destination="2")
        queue.enqueue(first, slot=0)
        queue.enqueue(second, slot=0)
        env._offloading_queues[("1", "2")] = queue
        env.trace = self._trace()
        env.current_slot = 1

        env.step(None)
        self.assertEqual(env._public_queues[("2", "1")].tasks[0].task_id, 1)
        self.assertEqual(env._offloading_queues[("1", "2")].tasks[0].task_id, 2)

    def test_source_indexed_public_queue_identity(self) -> None:
        topology = TopologyGraph(node_ids=("1", "2"), legal_adjacency={"1": ("2",)})
        env = self._env(topology=topology, compute_config=ComputeConfig(cpu_capacity_per_slot_agent=64.0, cpu_capacity_per_slot_edge=1.0, cpu_capacity_per_slot_cloud=1.0))
        trace = self._trace(TraceTaskBlueprint(task_id=3, source_agent_id=1, arrival_slot=0, size=2.0, processing_density=1.0, timeout_length=5, absolute_deadline_slot=5))
        env.trace = trace
        env._pending_arrivals = {0: [trace.tasks[0]]}  # type: ignore[assignment]
        env.current_slot = 0
        env._current_task = env._load_current_task()

        env.step("horizontal")
        env.step(None)
        self.assertIn(("2", "1"), env._public_queues)
        public_queue = env._public_queues[("2", "1")]
        self.assertEqual(public_queue.host_node_id, "2")
        self.assertEqual(public_queue.source_agent_id, "1")
        self.assertEqual(public_queue.tasks[0].queue_state, "public_queue")

    def test_cloud_public_queue_identity(self) -> None:
        topology = TopologyGraph(node_ids=("1", "cloud"), legal_adjacency={"1": ("cloud",)})
        env = self._env(topology=topology, compute_config=ComputeConfig(cpu_capacity_per_slot_agent=64.0, cpu_capacity_per_slot_edge=1.0, cpu_capacity_per_slot_cloud=1.0))
        trace = self._trace(TraceTaskBlueprint(task_id=4, source_agent_id=1, arrival_slot=0, size=2.0, processing_density=1.0, timeout_length=5, absolute_deadline_slot=5))
        env.trace = trace
        env._pending_arrivals = {0: [trace.tasks[0]]}  # type: ignore[assignment]
        env.current_slot = 0
        env._current_task = env._load_current_task()

        env.step("vertical")
        env.step(None)
        self.assertIn(("cloud", "1"), env._public_queues)
        public_queue = env._public_queues[("cloud", "1")]
        self.assertEqual(public_queue.host_node_id, "cloud")
        self.assertEqual(public_queue.source_agent_id, "1")

    def test_no_same_slot_public_execution_after_offload_admission(self) -> None:
        topology = TopologyGraph(node_ids=("1", "2"), legal_adjacency={"1": ("2",)})
        env = self._env(topology=topology, compute_config=ComputeConfig(cpu_capacity_per_slot_agent=64.0, cpu_capacity_per_slot_edge=1.0, cpu_capacity_per_slot_cloud=1.0))
        trace = self._trace(TraceTaskBlueprint(task_id=5, source_agent_id=1, arrival_slot=0, size=2.0, processing_density=1.0, timeout_length=5, absolute_deadline_slot=5))
        env.trace = trace
        env._pending_arrivals = {0: [trace.tasks[0]]}  # type: ignore[assignment]
        env.current_slot = 0
        env._current_task = env._load_current_task()

        env.step("horizontal")
        env.step(None)
        self.assertEqual(len(env._public_queues[("2", "1")].tasks), 1)
        self.assertEqual(env._public_queues[("2", "1")].tasks[0].queue_state, "public_queue")

    def test_public_cpu_sharing_uses_active_heads_at_slot_start(self) -> None:
        env = self._env(topology=TopologyGraph(node_ids=("1", "2", "3"), legal_adjacency={"1": ("2",), "3": ("2",)}), compute_config=ComputeConfig(cpu_capacity_per_slot_agent=64.0, cpu_capacity_per_slot_edge=8.0, cpu_capacity_per_slot_cloud=1.0))
        first = Task(task_id=6, source_agent_id=1, arrival_slot=0, size=64.0, processing_density=1.0, timeout_length=5, absolute_deadline_slot=5)
        second = Task(task_id=7, source_agent_id=3, arrival_slot=0, size=64.0, processing_density=1.0, timeout_length=5, absolute_deadline_slot=5)
        pq1 = PublicQueue(host_node_id="2", source_agent_id="1")
        pq2 = PublicQueue(host_node_id="2", source_agent_id="3")
        pq1.enqueue(first, slot=0)
        pq2.enqueue(second, slot=0)
        env._public_queues[("2", "1")] = pq1
        env._public_queues[("2", "3")] = pq2
        env.trace = self._trace()
        env.current_slot = 1

        env.step(None)

        self.assertEqual(first.metadata.get("capacity_sharing_active_heads"), 2)
        self.assertEqual(second.metadata.get("capacity_sharing_active_heads"), 2)
        self.assertEqual(float(first.metadata.get("capacity_sharing_allocated_capacity")), 4.0)

    def test_deadline_expiry_while_waiting_in_private_queue(self) -> None:
        env = self._env()
        trace = self._trace(
            TraceTaskBlueprint(task_id=8, source_agent_id=1, arrival_slot=0, size=128.0, processing_density=1.0, timeout_length=0, absolute_deadline_slot=0),
            TraceTaskBlueprint(task_id=9, source_agent_id=1, arrival_slot=0, size=128.0, processing_density=1.0, timeout_length=0, absolute_deadline_slot=0),
        )
        env.trace = trace
        env._pending_arrivals = {0: [trace.tasks[0], trace.tasks[1]]}  # type: ignore[assignment]
        env.current_slot = 0
        env._current_task = env._load_current_task()

        _obs0, _reward0, _terminated0, _truncated0, _info0 = env.step("local")
        _obs1, reward1, _terminated1, _truncated1, info1 = env.step("local")
        _obs2, reward2, _terminated2, _truncated2, info2 = env.step(None)

        self.assertTrue(any(task["terminal_outcome"] == "dropped" for task in info1["finalized_tasks"]))
        self.assertEqual(reward1, 0.0)
        self.assertLess(reward2, 0.0)
        self.assertFalse(any(task["terminal_outcome"] == "completed" for task in info2["finalized_tasks"]))

    def test_deadline_expiry_while_waiting_in_offloading_queue(self) -> None:
        topology = TopologyGraph(node_ids=("1", "2"), legal_adjacency={"1": ("2",)})
        env = self._env(topology=topology, compute_config=ComputeConfig(cpu_capacity_per_slot_agent=64.0, cpu_capacity_per_slot_edge=1.0, cpu_capacity_per_slot_cloud=1.0))
        task = Task(task_id=10, source_agent_id=1, arrival_slot=0, size=128.0, processing_density=1.0, timeout_length=0, absolute_deadline_slot=0)
        task.metadata["transmission_started_at"] = 0
        task.metadata["transmission_delay_slots"] = 1
        queue = OffloadingQueue(owner_node_id="1", resolved_destination="2")
        queue.enqueue(task, slot=0)
        env._offloading_queues[("1", "2")] = queue
        env.trace = self._trace()
        env.current_slot = 1

        _obs, _reward, _terminated, _truncated, info = env.step(None)
        self.assertTrue(any(task["terminal_outcome"] == "dropped" for task in info["finalized_tasks"]))
        self.assertIn(("2", "1"), env._public_queues)
        self.assertEqual(len(env._public_queues[("2", "1")].tasks), 0)

    def test_deadline_expiry_while_waiting_in_public_queue(self) -> None:
        env = self._env(topology=TopologyGraph(node_ids=("1", "2"), legal_adjacency={"1": ("2",)}), compute_config=ComputeConfig(cpu_capacity_per_slot_agent=64.0, cpu_capacity_per_slot_edge=1.0, cpu_capacity_per_slot_cloud=1.0))
        task = Task(task_id=11, source_agent_id=1, arrival_slot=0, size=128.0, processing_density=1.0, timeout_length=0, absolute_deadline_slot=0)
        public_queue = PublicQueue(host_node_id="2", source_agent_id="1")
        public_queue.enqueue(task, slot=0)
        env._public_queues[("2", "1")] = public_queue
        env.trace = self._trace()
        env.current_slot = 0

        _obs1, _reward1, _terminated1, _truncated1, info1 = env.step(None)
        _obs2, _reward2, _terminated2, _truncated2, info2 = env.step(None)
        self.assertTrue(any(task["terminal_outcome"] == "dropped" for task in info2["finalized_tasks"]))

    def test_termination_waits_for_delayed_reward(self) -> None:
        env = self._env()
        trace = self._trace(TraceTaskBlueprint(task_id=13, source_agent_id=1, arrival_slot=0, size=32.0, processing_density=1.0, timeout_length=5, absolute_deadline_slot=5))
        env.trace = trace
        env._pending_arrivals = {0: [trace.tasks[0]]}  # type: ignore[assignment]
        env.current_slot = 0
        env._current_task = env._load_current_task()

        _obs0, _reward0, terminated0, _truncated0, _info0 = env.step("local")
        self.assertFalse(terminated0)
        self.assertTrue(env._pending_terminal_tasks)
        _obs1, _reward1, terminated1, _truncated1, info1 = env.step(None)
        self.assertTrue(terminated1)
        self.assertFalse(_truncated1)
        self.assertTrue(info1["terminated"])


if __name__ == "__main__":
    unittest.main()
