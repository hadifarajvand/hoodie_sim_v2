from __future__ import annotations

import unittest

from src.dal.advisory import build_dal_advisory, build_dal_advisory_payload
from src.environment.compute_config import ComputeConfig
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.replay_hash import build_euls_replay_payload, stable_replay_hash
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.task import Task
from src.environment.topology import TopologyGraph
from src.evaluation.trace_protocol import EvaluationTrace, TraceTaskBlueprint


class DALAdvisoryLayerTests(unittest.TestCase):
    def _env(self) -> HoodieGymEnvironment:
        return HoodieGymEnvironment(
            episode_length=5,
            topology=TopologyGraph(node_ids=("1", "2", "cloud"), legal_adjacency={"1": ("2", "cloud")}),
            runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
            compute_config=ComputeConfig(cpu_capacity_per_slot_agent=64.0, cpu_capacity_per_slot_edge=2.0, cpu_capacity_per_slot_cloud=2.0),
            policy_name="FLC",
        )

    def _trace(self, deadline: int = 5) -> EvaluationTrace:
        return EvaluationTrace(
            trace_id="dal-trace",
            seed=11,
            tasks=(
                TraceTaskBlueprint(task_id=1, source_agent_id=1, arrival_slot=0, size=32.0, processing_density=1.0, timeout_length=deadline, absolute_deadline_slot=deadline),
            ),
            metadata={"mode": "deterministic_seed", "trace_id": "dal-trace", "seed": "11"},
        )

    def _prime(self, env: HoodieGymEnvironment, action: str = "local") -> None:
        trace = self._trace()
        env.trace = trace
        env._pending_arrivals = {0: [trace.tasks[0]]}  # type: ignore[assignment]
        env.current_slot = 0
        env._current_task = env._load_current_task()
        env.step(action)

    def test_dal_advisory_is_read_only(self) -> None:
        env = self._env()
        self._prime(env, "local")
        before_payload = build_euls_replay_payload(env)
        before_hash = stable_replay_hash(before_payload)

        advisory = build_dal_advisory_payload(env)
        self.assertTrue(advisory["advisory_notes"])

        after_payload = build_euls_replay_payload(env)
        after_hash = stable_replay_hash(after_payload)

        self.assertEqual(before_payload, after_payload)
        self.assertEqual(before_hash, after_hash)

    def test_dal_produces_deterministic_advisory(self) -> None:
        env = self._env()
        self._prime(env, "local")
        advisory_1 = build_dal_advisory(env)
        advisory_2 = build_dal_advisory(env)
        payload_1 = build_dal_advisory_payload(env)
        payload_2 = build_dal_advisory_payload(env)

        self.assertEqual(advisory_1, advisory_2)
        self.assertEqual(payload_1, payload_2)

    def test_deadline_pressure_labels_are_deterministic(self) -> None:
        env = self._env()
        env.trace = self._trace(deadline=10)
        env._pending_arrivals = {}  # type: ignore[assignment]
        env.current_slot = 0
        self.assertEqual(build_dal_advisory_payload(env, None)["deadline_pressure"], "none")

        env = self._env()
        env.trace = self._trace(deadline=0)
        env.current_slot = 1
        expired_task = Task(task_id=2, source_agent_id=1, arrival_slot=0, size=1.0, processing_density=1.0, timeout_length=0, absolute_deadline_slot=0)
        self.assertEqual(build_dal_advisory_payload(env, expired_task)["deadline_pressure"], "expired")

        env = self._env()
        env.trace = self._trace(deadline=1)
        env.current_slot = 0
        env._current_task = Task(task_id=3, source_agent_id=1, arrival_slot=0, size=1.0, processing_density=1.0, timeout_length=1, absolute_deadline_slot=1)
        self.assertEqual(build_dal_advisory_payload(env, env._current_task)["deadline_pressure"], "critical")

        env = self._env()
        env.trace = self._trace(deadline=3)
        env.current_slot = 0
        env._current_task = Task(task_id=4, source_agent_id=1, arrival_slot=0, size=1.0, processing_density=1.0, timeout_length=3, absolute_deadline_slot=3)
        self.assertEqual(build_dal_advisory_payload(env, env._current_task)["deadline_pressure"], "high")

        env = self._env()
        env.trace = self._trace(deadline=6)
        env.current_slot = 0
        env._current_task = Task(task_id=5, source_agent_id=1, arrival_slot=0, size=1.0, processing_density=1.0, timeout_length=6, absolute_deadline_slot=6)
        self.assertEqual(build_dal_advisory_payload(env, env._current_task)["deadline_pressure"], "medium")

        env = self._env()
        env.trace = self._trace(deadline=12)
        env.current_slot = 0
        env._current_task = Task(task_id=6, source_agent_id=1, arrival_slot=0, size=1.0, processing_density=1.0, timeout_length=12, absolute_deadline_slot=12)
        self.assertEqual(build_dal_advisory_payload(env, env._current_task)["deadline_pressure"], "low")

    def test_queue_pressure_counts_match_euls_queues(self) -> None:
        env = self._env()
        self._prime(env, "horizontal")
        advisory = build_dal_advisory_payload(env)
        self.assertEqual(advisory["private_queue_load"], 0)
        self.assertGreaterEqual(advisory["offloading_queue_load"], 1)
        self.assertGreaterEqual(advisory["total_queue_load"], advisory["offloading_queue_load"])

    def test_dal_does_not_alter_action_mask_or_selected_action(self) -> None:
        env = self._env()
        env.reset(seed=7)
        before_mask = env.legal_action_mask(env.current_task)
        before_selected = env.current_task.selected_action if env.current_task is not None else None
        build_dal_advisory_payload(env)
        after_mask = env.legal_action_mask(env.current_task)
        after_selected = env.current_task.selected_action if env.current_task is not None else None
        self.assertEqual(before_mask, after_mask)
        self.assertEqual(before_selected, after_selected)

    def test_dal_is_replay_compatible(self) -> None:
        env = self._env()
        self._prime(env, "vertical")
        before_hash = stable_replay_hash(build_euls_replay_payload(env))
        build_dal_advisory_payload(env)
        after_hash = stable_replay_hash(build_euls_replay_payload(env))
        self.assertEqual(before_hash, after_hash)


if __name__ == "__main__":
    unittest.main()
