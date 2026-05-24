from __future__ import annotations

import unittest

from src.environment.compute_config import ComputeConfig
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.lifecycle_trace import LifecycleTraceConfig
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph


class PassiveSelectedActionTraceRepairIntegrationTest(unittest.TestCase):
    def test_decision_point_emits_selected_action_join_fields(self) -> None:
        topology = TopologyGraph(node_ids=("1", "2", "cloud"), legal_adjacency={"1": ("2", "cloud")})
        env = HoodieGymEnvironment(
            episode_length=3,
            topology=topology,
            runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
            compute_config=ComputeConfig(cpu_capacity_per_slot_agent=64.0, cpu_capacity_per_slot_edge=64.0, cpu_capacity_per_slot_cloud=64.0),
            trace_config=LifecycleTraceConfig(trace_enabled=True),
            policy_name="FLC",
        )
        env.reset(seed=7)
        current_task = env.current_task
        self.assertIsNotNone(current_task)
        _obs, _reward, _terminated, _truncated, info = env.step("horizontal")

        events = [event for event in info["lifecycle_trace_events"] if event["event_type"] == "task_admitted"]
        self.assertTrue(events)
        emitted = events[0]
        self.assertEqual(emitted["selected_action"], "horizontal")
        self.assertEqual(emitted["selected_action_family"], "horizontal")
        self.assertEqual(emitted["selected_action_trace_source"], "decision_point")
        self.assertEqual(emitted["selected_action_to_task_join_key"], f"{info['trace_id']}:{current_task.task_id}")
        self.assertEqual(emitted["terminal_outcome_join_key"], f"{info['trace_id']}:{current_task.task_id}:terminal_outcome")
        self.assertEqual(emitted["decision_event_id"], f"{info['trace_id']}:{info['slot'] - 1}:{current_task.task_id}")


if __name__ == "__main__":
    unittest.main()
