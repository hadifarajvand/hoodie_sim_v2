from __future__ import annotations

import unittest

from src.environment.compute_config import ComputeConfig
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.link_rate_config import compute_transmission_delay, mbits_to_bits
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph
from src.evaluation.trace_protocol import EvaluationTrace, TraceTaskBlueprint


class TransmissionDelayRuntimeWiringIntegrationTests(unittest.TestCase):
    def _trace(self, *, task_id: int, size: float, processing_density: float = 0.1, deadline: int = 20) -> EvaluationTrace:
        return EvaluationTrace(
            trace_id=f"transmission-delay-{task_id}",
            seed=104,
            tasks=(
                TraceTaskBlueprint(
                    task_id=task_id,
                    source_agent_id=1,
                    arrival_slot=0,
                    size=size,
                    processing_density=processing_density,
                    timeout_length=deadline,
                    absolute_deadline_slot=deadline,
                ),
            ),
            metadata={"mode": "deterministic_seed", "trace_id": f"transmission-delay-{task_id}", "seed": "104"},
        )

    def _environment(self, trace: EvaluationTrace, topology: TopologyGraph) -> HoodieGymEnvironment:
        env = HoodieGymEnvironment(
            episode_length=10,
            topology=topology,
            runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
            compute_config=ComputeConfig(cpu_capacity_per_slot_agent=10.0, cpu_capacity_per_slot_edge=10.0, cpu_capacity_per_slot_cloud=10.0),
            policy_name="HOODIE",
        )
        env.trace = trace
        env._pending_arrivals = {0: [trace.tasks[0]]}  # type: ignore[assignment]
        env.current_slot = 0
        env._current_task = env._load_current_task()
        return env

    def test_horizontal_transmission_delay_uses_task_size_and_RH(self) -> None:
        trace = self._trace(task_id=11, size=3.0)
        env = self._environment(trace, TopologyGraph(node_ids=("1", "2"), legal_adjacency={"1": ("2",)}))

        _obs, _reward, _terminated, _truncated, _info = env.step("horizontal")
        source_id = "1"
        destination = "2"
        queue = env._offloading_queues[(source_id, destination)]
        task = queue.tasks[0]
        expected = compute_transmission_delay(
            mbits_to_bits(3.0),
            env.link_rate_config.horizontal_data_rate_bps,
            slot_duration_seconds=env.link_rate_config.slot_duration_seconds,
            rounding_policy=env.link_rate_config.rounding_policy,
        )

        self.assertEqual(task.metadata["transmission_payload_bits"], mbits_to_bits(3.0))
        self.assertEqual(task.metadata["transmission_data_rate_bps"], env.link_rate_config.horizontal_data_rate_bps)
        self.assertEqual(task.metadata["transmission_delay_slots"], expected.delay_slots)
        self.assertEqual(task.metadata["transmission_rounding_policy"], env.link_rate_config.rounding_policy)
        self.assertEqual(task.metadata["transmission_rate_source"], "horizontal_R_H")
        self.assertEqual(queue.tasks[0].metadata["transmission_started_at"], 0)
        self.assertEqual(len(env._public_queues[(destination, source_id)].tasks), 0)

    def test_vertical_transmission_delay_uses_task_size_and_RV(self) -> None:
        trace = self._trace(task_id=12, size=3.0)
        env = self._environment(trace, TopologyGraph(node_ids=("1", "cloud"), legal_adjacency={"1": ("cloud",)}))

        _obs, _reward, _terminated, _truncated, _info = env.step("vertical")
        source_id = "1"
        destination = "cloud"
        queue = env._offloading_queues[(source_id, destination)]
        task = queue.tasks[0]
        expected = compute_transmission_delay(
            mbits_to_bits(3.0),
            env.link_rate_config.vertical_data_rate_bps,
            slot_duration_seconds=env.link_rate_config.slot_duration_seconds,
            rounding_policy=env.link_rate_config.rounding_policy,
        )

        self.assertEqual(task.metadata["transmission_payload_bits"], mbits_to_bits(3.0))
        self.assertEqual(task.metadata["transmission_data_rate_bps"], env.link_rate_config.vertical_data_rate_bps)
        self.assertEqual(task.metadata["transmission_delay_slots"], expected.delay_slots)
        self.assertEqual(task.metadata["transmission_rounding_policy"], env.link_rate_config.rounding_policy)
        self.assertEqual(task.metadata["transmission_rate_source"], "vertical_R_V")

    def test_vertical_delay_exceeds_horizontal_delay_for_same_payload(self) -> None:
        payload_bits = mbits_to_bits(3.0)
        horizontal = compute_transmission_delay(
            payload_bits,
            30_000_000.0,
            slot_duration_seconds=0.1,
            rounding_policy="ceil",
        )
        vertical = compute_transmission_delay(
            payload_bits,
            10_000_000.0,
            slot_duration_seconds=0.1,
            rounding_policy="ceil",
        )

        self.assertGreater(vertical.delay_slots, horizontal.delay_slots)

    def test_offload_not_admitted_before_delay_boundary(self) -> None:
        trace = self._trace(task_id=13, size=6.0)
        env = self._environment(trace, TopologyGraph(node_ids=("1", "2"), legal_adjacency={"1": ("2",)}))

        env.step("horizontal")
        self.assertEqual(len(env._offloading_queues[("1", "2")].tasks), 1)
        self.assertEqual(len(env._public_queues[("2", "1")].tasks), 0)

        _obs, reward, _terminated, _truncated, info = env.step(None)
        self.assertEqual(reward, 0.0)
        self.assertFalse(info["finalized_tasks"])
        self.assertEqual(len(env._offloading_queues[("1", "2")].tasks), 1)
        self.assertEqual(len(env._public_queues[("2", "1")].tasks), 0)

    def test_offload_admitted_at_documented_boundary(self) -> None:
        trace = self._trace(task_id=14, size=3.0)
        env = HoodieGymEnvironment(
            episode_length=10,
            topology=TopologyGraph(node_ids=("1", "2"), legal_adjacency={"1": ("2",)}),
            runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
            compute_config=ComputeConfig(cpu_capacity_per_slot_agent=0.01, cpu_capacity_per_slot_edge=0.01, cpu_capacity_per_slot_cloud=0.01),
            policy_name="HOODIE",
        )
        env.trace = trace
        env._pending_arrivals = {0: [trace.tasks[0]]}  # type: ignore[assignment]
        env.current_slot = 0
        env._current_task = env._load_current_task()

        env.step("horizontal")
        env.step(None)
        self.assertIn(("2", "1"), env._public_queues)
        admitted_task = env._public_queues[("2", "1")].tasks[0]

        self.assertEqual(admitted_task.metadata["transmission_completed_at"], 1)
        self.assertEqual(admitted_task.metadata["public_queue_admitted_at"], 1)

    def test_horizontal_metadata_recorded(self) -> None:
        trace = self._trace(task_id=15, size=3.0)
        env = HoodieGymEnvironment(
            episode_length=10,
            topology=TopologyGraph(node_ids=("1", "2"), legal_adjacency={"1": ("2",)}),
            runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
            compute_config=ComputeConfig(cpu_capacity_per_slot_agent=0.01, cpu_capacity_per_slot_edge=0.01, cpu_capacity_per_slot_cloud=0.01),
            policy_name="HOODIE",
        )
        env.trace = trace
        env._pending_arrivals = {0: [trace.tasks[0]]}  # type: ignore[assignment]
        env.current_slot = 0
        env._current_task = env._load_current_task()

        env.step("horizontal")
        env.step(None)
        task = env._public_queues[("2", "1")].tasks[0]

        self.assertEqual(task.metadata["transmission_started_at"], 0)
        self.assertEqual(task.metadata["transmission_completed_at"], 1)
        self.assertEqual(task.metadata["transmission_rounding_policy"], env.link_rate_config.rounding_policy)

    def test_vertical_metadata_recorded(self) -> None:
        trace = self._trace(task_id=16, size=3.0)
        env = self._environment(trace, TopologyGraph(node_ids=("1", "cloud"), legal_adjacency={"1": ("cloud",)}))

        env.step("vertical")
        task = env._offloading_queues[("1", "cloud")].tasks[0]

        self.assertEqual(task.metadata["transmission_started_at"], 0)
        self.assertEqual(task.metadata["transmission_rate_source"], "vertical_R_V")
        self.assertNotIn("transmission_completed_at", task.metadata)

    def test_local_path_has_no_transmission_metadata(self) -> None:
        trace = self._trace(task_id=17, size=1.0)
        env = HoodieGymEnvironment(
            episode_length=10,
            runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
            compute_config=ComputeConfig(cpu_capacity_per_slot_agent=0.01),
            policy_name="HOODIE",
        )
        env.trace = trace
        env._pending_arrivals = {0: [trace.tasks[0]]}  # type: ignore[assignment]
        env.current_slot = 0
        env._current_task = env._load_current_task()

        env.step("local")
        task = env._private_queues["1"].tasks[0]
        transmission_keys = [key for key in task.metadata if key.startswith("transmission_")]
        self.assertEqual(transmission_keys, [])

    def test_reward_not_emitted_during_transmission(self) -> None:
        trace = self._trace(task_id=18, size=3.0)
        env = self._environment(trace, TopologyGraph(node_ids=("1", "cloud"), legal_adjacency={"1": ("cloud",)}))

        env.step("vertical")
        _obs, reward, _terminated, _truncated, info = env.step(None)

        self.assertEqual(reward, 0.0)
        self.assertFalse(info["finalized_tasks"])

    def test_timeout_drop_includes_transmission_delay(self) -> None:
        trace = self._trace(task_id=19, size=3.0, processing_density=0.1, deadline=2)
        env = self._environment(trace, TopologyGraph(node_ids=("1", "cloud"), legal_adjacency={"1": ("cloud",)}))

        env.step("vertical")
        env.step(None)
        env.step(None)
        _obs, reward, _terminated, _truncated, info = env.step(None)

        self.assertEqual(info["finalized_tasks"][0]["terminal_outcome"], "dropped")
        self.assertLess(reward, 0.0)
        self.assertTrue(info["finalized_tasks"][0]["offload_lifecycle_events"])

    def test_no_feature_033_execution_contract_drift(self) -> None:
        trace = self._trace(task_id=20, size=3.0)
        env = self._environment(trace, TopologyGraph(node_ids=("1", "2"), legal_adjacency={"1": ("2",)}))

        env.step("horizontal")
        task = env._offloading_queues[("1", "2")].tasks[0]
        self.assertEqual(task.metadata["transmission_delay_slots"], 1)
        self.assertEqual(env.compute_config.cpu_capacity_per_slot_agent, 10.0)

    def test_no_dependency_training_policy_campaign_drift(self) -> None:
        trace = self._trace(task_id=21, size=1.0)
        env = self._environment(trace, TopologyGraph(node_ids=("1", "2"), legal_adjacency={"1": ("2",)}))

        self.assertTrue(env.link_rate_config.horizontal_data_rate_bps > 0)
        self.assertTrue(env.link_rate_config.vertical_data_rate_bps > 0)
        self.assertEqual(env.runtime_parameters.runtime_variant, "constant_service")


if __name__ == "__main__":
    unittest.main()
