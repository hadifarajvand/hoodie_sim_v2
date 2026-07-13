from __future__ import annotations

import unittest

from src.environment.compute_config import ComputeConfig
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.topology import TopologyGraph
from src.evaluation.trace_protocol import EvaluationTrace, TraceTaskBlueprint


class GymEnvironmentEventLedgerIntegrationTests(unittest.TestCase):
    def _env(self) -> HoodieGymEnvironment:
        return HoodieGymEnvironment(
            episode_length=24,
            topology=TopologyGraph(node_ids=("1", "2", "cloud"), legal_adjacency={"1": ("2", "cloud")}),
            runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
            compute_config=ComputeConfig(cpu_capacity_per_slot_agent=64.0, cpu_capacity_per_slot_edge=64.0, cpu_capacity_per_slot_cloud=64.0),
            policy_name="FLC",
        )

    def test_resolution_reward_and_admission_events_remain_separate(self) -> None:
        env = self._env()
        trace = EvaluationTrace(
            trace_id="event-ledger",
            seed=7,
            tasks=(
                TraceTaskBlueprint(task_id=1, source_agent_id=1, arrival_slot=0, size=16.0, processing_density=1.0, timeout_length=8, absolute_deadline_slot=8),
                TraceTaskBlueprint(task_id=2, source_agent_id=1, arrival_slot=0, size=32.0, processing_density=1.0, timeout_length=20, absolute_deadline_slot=20),
                TraceTaskBlueprint(task_id=3, source_agent_id=1, arrival_slot=0, size=3.0, processing_density=1.0, timeout_length=2, absolute_deadline_slot=0),
            ),
            metadata={"mode": "deterministic_seed", "trace_id": "event-ledger", "seed": "7"},
        )
        env.trace = trace
        env._pending_arrivals = {0: [trace.tasks[0], trace.tasks[1], trace.tasks[2]]}  # type: ignore[assignment]
        env.current_slot = 0
        env._current_task = env._load_current_task()

        resolution_events: list[dict[str, object]] = []
        reward_delivery_events: list[dict[str, object]] = []
        finalized_ids: list[int] = []
        reward_by_task: dict[int, float] = {}
        for step_index in range(20):
            current_task = env.current_task
            if current_task is None:
                action = None
            elif current_task.task_id == 1:
                action = "local"
            elif current_task.task_id == 2:
                action = "horizontal"
            else:
                action = "vertical"
            _obs, reward, terminated, truncated, info = env.step(action)
            resolution_events.extend(info["task_resolution_events"])
            reward_delivery_events.extend(info["reward_delivery_events"])
            finalized_ids.extend(task["task_id"] for task in info["finalized_tasks"])
            for event in info["reward_delivery_events"]:
                reward_by_task[int(event["task_id"])] = float(event["reward"])
            if terminated or truncated:
                break

        self.assertEqual(sorted(set(finalized_ids)), [1, 2, 3])
        self.assertEqual(sorted(event["task_id"] for event in resolution_events), [1, 2, 3])
        self.assertEqual(sorted(event["task_id"] for event in reward_delivery_events), [1, 2, 3])
        self.assertEqual(len({event["task_id"] for event in resolution_events}), len(resolution_events))
        self.assertEqual(len({event["task_id"] for event in reward_delivery_events}), len(reward_delivery_events))
        self.assertTrue(all(event["resolution_slot"] <= event["delivery_slot"] for event in reward_delivery_events))
        self.assertTrue(any(event["outcome"] == "drop" for event in resolution_events))
        self.assertEqual(sum(1 for event in resolution_events if event["outcome"] == "success") + sum(1 for event in resolution_events if event["outcome"] == "drop"), 3)
        self.assertEqual(sum(1 for event in reward_delivery_events if event["reward"] < 0.0), 3)
        self.assertFalse(env._pending_reward_tasks)
        self.assertFalse(env._pending_reward_ledger)
        self.assertEqual(set(reward_by_task), {1, 2, 3})


if __name__ == "__main__":
    unittest.main()
