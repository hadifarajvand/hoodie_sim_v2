from __future__ import annotations

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
from src.environment.traffic_observer import TrafficObserver
from src.policies.adaptive_offloading import AdaptiveOffloadingPolicy
from src.policies.policy_interface import PolicyContext


class AdaptivePolicyEnvironmentFlowTests(unittest.TestCase):
    def test_adaptive_policy_runs_through_environment_boundary(self) -> None:
        config = TrafficConfig(
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
        trace = TrafficGenerator.generate(config, seed=7)
        summary = TrafficObserver.summarize(trace.evaluation_trace, config, seed=7)

        with tempfile.TemporaryDirectory() as tmpdir:
            trace_root = Path(tmpdir)
            trace.write_json(trace_root / f"{trace.trace_id}.json")
            env = HoodieGymEnvironment(
                episode_length=3,
                topology=TopologyGraph(node_ids=("1",), legal_adjacency={"1": ()}),
                runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
                compute_config=ComputeConfig(cpu_capacity_per_slot_agent=1.0),
                trace_source=TraceSource.from_trace_bank(trace.trace_id, root_path=trace_root),
                policy_name="Adaptive",
            )

            observation, info = env.reset(seed=None)
            self.assertEqual(info["trace_id"], trace.trace_id)
            self.assertEqual(list(observation.keys()), ["1"])
            self.assertFalse(hasattr(env.engine, "run_slot"))
            self.assertFalse(hasattr(env.engine, "slot_flow"))

            policy = AdaptiveOffloadingPolicy()
            final_info: dict[str, object] = {}
            seen_finalization = False

            while True:
                current_task = env.current_task
                if current_task is None:
                    action = None
                else:
                    enriched_observation = env.observe_flat(current_task)
                    enriched_observation["traffic_summary"] = {
                        "scenario_name": summary.scenario_name,
                        "seed": summary.seed,
                        "configured_arrival_probability": summary.configured_arrival_probability,
                        "observed_arrival_probability": summary.observed_arrival_probability,
                        "total_arrivals": summary.total_arrivals,
                        "arrivals_per_slot": summary.arrivals_per_slot,
                        "arrivals_per_agent": summary.arrivals_per_agent,
                    }
                    context = PolicyContext(
                        observation=enriched_observation,
                        legal_action_mask=env.legal_action_mask(current_task),
                        trace_history=(trace.trace_id,),
                    )
                    action = policy.choose_action(context)
                    self.assertEqual(action, "local")
                observation, reward, terminated, truncated, final_info = env.step(action)
                if final_info["finalized_tasks"]:
                    seen_finalization = True
                    self.assertEqual(final_info["finalized_tasks"][0]["terminal_outcome"], "completed")
                    self.assertEqual(final_info["finalized_tasks"][0]["selected_action"], "local")
                if terminated or truncated:
                    break

            self.assertTrue(terminated or truncated)
            self.assertTrue(seen_finalization)
            self.assertEqual(final_info["trace_id"], trace.trace_id)
            self.assertTrue(final_info["finalized_tasks"])

    def test_environment_remains_policy_agnostic(self) -> None:
        self.assertFalse(hasattr(HoodieGymEnvironment, "choose_action"))
        self.assertFalse(hasattr(HoodieGymEnvironment, "adaptive_step"))


if __name__ == "__main__":
    unittest.main()
