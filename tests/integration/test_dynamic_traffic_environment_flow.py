from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph
from src.environment.trace_source import TraceSource
from src.environment.traffic_config import TrafficConfig
from src.environment.traffic_generator import TrafficGenerator
from src.policies.flc import FullLocalComputingPolicy
from src.policies.policy_interface import PolicyContext


class DynamicTrafficEnvironmentFlowTests(unittest.TestCase):
    def _config(self) -> TrafficConfig:
        return TrafficConfig(
            scenario_name="paper_default",
            number_of_agents=3,
            episode_length=3,
            arrival_probability=1.0,
            slot_duration_seconds=0.1,
            timeout_slots=20,
            task_size_mbits_min=2.0,
            task_size_mbits_max=2.2,
            task_size_mbits_step=0.1,
            processing_density_gcycles_per_mbit=0.297,
        )

    def test_generated_trace_runs_through_environment_boundary(self) -> None:
        config = self._config()
        traffic_trace = TrafficGenerator.generate(config, seed=42)

        with tempfile.TemporaryDirectory() as tmpdir:
            trace_root = Path(tmpdir)
            traffic_trace.write_json(trace_root / f"{traffic_trace.trace_id}.json")
            env = HoodieGymEnvironment(
                episode_length=config.episode_length,
                runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
                trace_source=TraceSource.from_trace_bank(traffic_trace.trace_id, root_path=trace_root),
                policy_name="FLC",
            )

            observation, info = env.reset(seed=None)
            policy = FullLocalComputingPolicy()
            finalized_task_ids: list[int] = []

            self.assertEqual(info["trace_id"], traffic_trace.trace_id)
            self.assertEqual(list(observation.keys()), ["1"])

            while True:
                current_task = env.current_task
                action = None if current_task is None else policy.choose_action(
                    PolicyContext(
                        observation=env.observe_flat(current_task),
                        legal_action_mask=env.legal_action_mask(current_task),
                        trace_history=(traffic_trace.trace_id,),
                    )
                )
                observation, reward, terminated, truncated, step_info = env.step(action)
                finalized_task_ids.extend(int(task["task_id"]) for task in step_info["finalized_tasks"])
                if terminated or truncated:
                    break

            self.assertGreater(len(finalized_task_ids), 0)
            self.assertTrue(terminated or truncated)
            self.assertEqual(step_info["trace_id"], traffic_trace.trace_id)

    def test_same_slot_multi_agent_arrivals_are_serialized_deterministically(self) -> None:
        config = self._config()
        traffic_trace = TrafficGenerator.generate(config, seed=99)

        with tempfile.TemporaryDirectory() as tmpdir:
            trace_root = Path(tmpdir)
            traffic_trace.write_json(trace_root / f"{traffic_trace.trace_id}.json")
            env = HoodieGymEnvironment(
                episode_length=config.episode_length,
                runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
                trace_source=TraceSource.from_trace_bank(traffic_trace.trace_id, root_path=trace_root),
                policy_name="FLC",
            )

            env.reset(seed=None)
            policy = FullLocalComputingPolicy()
            presented_agent_ids: list[int] = []

            for _ in range(3):
                self.assertIsNotNone(env.current_task)
                presented_agent_ids.append(env.current_task.source_agent_id)
                current_task = env.current_task
                action = policy.choose_action(
                    PolicyContext(
                        observation=env.observe_flat(current_task),
                        legal_action_mask=env.legal_action_mask(current_task),
                        trace_history=(traffic_trace.trace_id,),
                    )
                )
                env.step(action)

            self.assertEqual(presented_agent_ids, [1, 2, 3])

    def test_fractional_paper_values_survive_json_trace_and_env_reset(self) -> None:
        config = TrafficConfig(
            scenario_name="paper_default",
            number_of_agents=1,
            episode_length=1,
            arrival_probability=1.0,
            slot_duration_seconds=0.1,
            timeout_slots=20,
            task_size_mbits_min=2.0,
            task_size_mbits_max=2.1,
            task_size_mbits_step=0.1,
            processing_density_gcycles_per_mbit=0.297,
        )
        traffic_trace = TrafficGenerator.generate(config, seed=1)

        with tempfile.TemporaryDirectory() as tmpdir:
            trace_root = Path(tmpdir)
            payload_path = trace_root / f"{traffic_trace.trace_id}.json"
            traffic_trace.write_json(payload_path)
            payload = payload_path.read_text(encoding="utf-8")
            self.assertIn('"size": 2.1', payload)
            self.assertIn('"processing_density": 0.297', payload)
            self.assertIn('"cycles_required"', payload)
            self.assertIn('"cycles_remaining"', payload)

            env = HoodieGymEnvironment(
                episode_length=config.episode_length,
                runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
                trace_source=TraceSource.from_trace_bank(traffic_trace.trace_id, root_path=trace_root),
                policy_name="FLC",
            )

            observation, info = env.reset(seed=None)

            self.assertEqual(info["trace_id"], traffic_trace.trace_id)
            self.assertEqual(list(observation.keys()), ["1"])
            self.assertEqual(env.current_task.size, 2.1)
            self.assertEqual(env.current_task.processing_density, 0.297)
            self.assertAlmostEqual(env.current_task.cycles_required, 2.1 * 0.297)
            self.assertAlmostEqual(env.current_task.cycles_remaining, 2.1 * 0.297)


if __name__ == "__main__":
    unittest.main()
