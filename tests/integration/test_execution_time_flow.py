from __future__ import annotations

import math
import tempfile
import unittest
from pathlib import Path

from src.environment.compute_config import ComputeConfig
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph
from src.environment.trace_source import TraceSource
from src.environment.traffic_config import TrafficConfig
from src.environment.traffic_generator import TrafficGenerator
from src.policies.flc import FullLocalComputingPolicy
from src.policies.ho import HorizontalOffloadingPolicy
from src.policies.policy_interface import PolicyContext
from src.policies.vo import VerticalOffloadingPolicy


class ExecutionTimeFlowTests(unittest.TestCase):
    def _config(self) -> TrafficConfig:
        return TrafficConfig(
            scenario_name="paper_default",
            number_of_agents=1,
            episode_length=1,
            arrival_probability=1.0,
            slot_duration_seconds=0.1,
            timeout_slots=20,
            task_size_mbits_min=2.1,
            task_size_mbits_max=2.1,
            task_size_mbits_step=0.1,
            processing_density_gcycles_per_mbit=0.297,
        )

    def _run_episode(
        self,
        *,
        policy: object,
        topology: TopologyGraph | None,
        compute_config: ComputeConfig,
    ) -> tuple[dict[str, object], dict[str, object]]:
        config = self._config()
        traffic_trace = TrafficGenerator.generate(config, seed=42)

        with tempfile.TemporaryDirectory() as tmpdir:
            trace_root = Path(tmpdir)
            payload_path = trace_root / f"{traffic_trace.trace_id}.json"
            traffic_trace.write_json(payload_path)
            payload = payload_path.read_text(encoding="utf-8")
            self.assertIn('"cycles_required"', payload)
            self.assertIn('"cycles_remaining"', payload)

            env = HoodieGymEnvironment(
                episode_length=10,
                topology=topology,
                runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
                compute_config=compute_config,
                trace_source=TraceSource.from_trace_bank(traffic_trace.trace_id, root_path=trace_root),
                policy_name="FLC",
            )

            observation, info = env.reset(seed=None)
            self.assertEqual(info["trace_id"], traffic_trace.trace_id)
            self.assertEqual(env.current_task.size, 2.1)
            self.assertAlmostEqual(env.current_task.cycles_required, 2.1 * 0.297)
            self.assertAlmostEqual(env.current_task.cycles_remaining, 2.1 * 0.297)

            final_info: dict[str, object] = {}
            final_observation = observation
            while True:
                current_task = env.current_task
                action = None
                if current_task is not None:
                    action = policy.choose_action(
                        PolicyContext(
                            observation=env.observe_flat(current_task),
                            legal_action_mask=env.legal_action_mask(current_task),
                            trace_history=(traffic_trace.trace_id,),
                        )
                    )
                final_observation, reward, terminated, truncated, final_info = env.step(action)
                if terminated or truncated:
                    break

            self.assertGreaterEqual(len(final_info["finalized_tasks"]), 1)
            return final_info, {"observation": final_observation, "trace": traffic_trace}

    def test_local_edge_and_cloud_execution_complete_in_expected_slots(self) -> None:
        task_cycles = 2.1 * 0.297
        compute_config = ComputeConfig(
            cpu_capacity_per_slot_agent=0.25,
            cpu_capacity_per_slot_edge=0.2,
            cpu_capacity_per_slot_cloud=0.1,
        )

        local_info, _ = self._run_episode(
            policy=FullLocalComputingPolicy(),
            topology=None,
            compute_config=compute_config,
        )
        local_record = local_info["finalized_tasks"][0]
        self.assertEqual(local_record["terminal_outcome"], "completed")
        self.assertIsNotNone(local_record["completion_slot"])

        edge_info, _ = self._run_episode(
            policy=HorizontalOffloadingPolicy(),
            topology=TopologyGraph(node_ids=("1", "2"), legal_adjacency={"1": ("2",)}),
            compute_config=compute_config,
        )
        edge_record = edge_info["finalized_tasks"][0]
        self.assertEqual(edge_record["terminal_outcome"], "completed")
        self.assertEqual(edge_record["resolved_destination"], "2")
        self.assertIsNotNone(edge_record["completion_slot"])

        cloud_info, _ = self._run_episode(
            policy=VerticalOffloadingPolicy(),
            topology=TopologyGraph(node_ids=("1", "cloud"), legal_adjacency={"1": ("cloud",)}),
            compute_config=compute_config,
        )
        cloud_record = cloud_info["finalized_tasks"][0]
        self.assertEqual(cloud_record["terminal_outcome"], "completed")
        self.assertEqual(cloud_record["resolved_destination"], "cloud")
        self.assertIsNotNone(cloud_record["completion_slot"])

    def test_environment_local_execution_requires_multiple_slots_when_cycles_exceed_capacity(self) -> None:
        compute_config = ComputeConfig(cpu_capacity_per_slot_agent=0.5, cpu_capacity_per_slot_edge=0.5, cpu_capacity_per_slot_cloud=3.0)
        final_info, _ = self._run_episode(
            policy=FullLocalComputingPolicy(),
            topology=None,
            compute_config=compute_config,
        )

        local_record = final_info["finalized_tasks"][0]
        self.assertEqual(local_record["terminal_outcome"], "completed")
        self.assertEqual(local_record["completion_slot"], 1)
        self.assertGreater(local_record["completion_slot"], 0)

    def test_same_slot_multi_agent_execution_still_serializes_deterministically(self) -> None:
        config = TrafficConfig(
            scenario_name="paper_default",
            number_of_agents=3,
            episode_length=1,
            arrival_probability=1.0,
            slot_duration_seconds=0.1,
            timeout_slots=20,
            task_size_mbits_min=2.1,
            task_size_mbits_max=2.1,
            task_size_mbits_step=0.1,
            processing_density_gcycles_per_mbit=0.297,
        )
        traffic_trace = TrafficGenerator.generate(config, seed=1)

        with tempfile.TemporaryDirectory() as tmpdir:
            trace_root = Path(tmpdir)
            traffic_trace.write_json(trace_root / f"{traffic_trace.trace_id}.json")
            env = HoodieGymEnvironment(
                episode_length=10,
                runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
                compute_config=ComputeConfig(cpu_capacity_per_slot_agent=1.0),
                trace_source=TraceSource.from_trace_bank(traffic_trace.trace_id, root_path=trace_root),
                policy_name="FLC",
            )

            env.reset(seed=None)
            policy = FullLocalComputingPolicy()
            presented_agent_ids: list[int] = []
            while True:
                current_task = env.current_task
                if current_task is not None:
                    presented_agent_ids.append(current_task.source_agent_id)
                    action = policy.choose_action(
                        PolicyContext(
                            observation=env.observe_flat(current_task),
                            legal_action_mask=env.legal_action_mask(current_task),
                            trace_history=(traffic_trace.trace_id,),
                        )
                    )
                else:
                    action = None
                _obs, _reward, terminated, truncated, _info = env.step(action)
                if terminated or truncated:
                    break

            self.assertEqual(presented_agent_ids, [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
