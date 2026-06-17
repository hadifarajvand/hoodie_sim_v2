from __future__ import annotations

import unittest

from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.runtime_model import SharedRuntimeParameters
from src.evaluation.trace_protocol import EvaluationTrace, TraceTaskBlueprint


class EnvironmentLifecycleRepairUnitTest(unittest.TestCase):
    def _environment(self, trace: EvaluationTrace) -> HoodieGymEnvironment:
        env = HoodieGymEnvironment(
            episode_length=6,
            runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
            policy_name="HOODIE",
        )
        env.trace = trace
        pending: dict[int, list[TraceTaskBlueprint]] = {}
        for blueprint in trace.tasks:
            pending.setdefault(blueprint.arrival_slot, []).append(blueprint)
        for blueprints in pending.values():
            blueprints.sort(key=lambda item: (item.arrival_slot, item.source_agent_id, item.task_id))
        env._pending_arrivals = pending  # type: ignore[assignment]
        env.current_slot = 0
        env._current_task = env._load_current_task()
        return env

    def _single_task_trace(self, *, task_id: int, arrival_slot: int, timeout_slot: int, size: float, density: float) -> EvaluationTrace:
        return EvaluationTrace(
            trace_id=f"repair-{task_id}",
            seed=task_id,
            tasks=(
                TraceTaskBlueprint(
                    task_id=task_id,
                    source_agent_id=1,
                    arrival_slot=arrival_slot,
                    size=size,
                    processing_density=density,
                    timeout_length=timeout_slot,
                    absolute_deadline_slot=timeout_slot,
                ),
            ),
            metadata={"mode": "deterministic_seed", "trace_id": f"repair-{task_id}", "seed": str(task_id)},
        )

    def test_local_compute_completes_before_timeout_when_deadline_allows(self) -> None:
        env = self._environment(self._single_task_trace(task_id=11, arrival_slot=0, timeout_slot=5, size=0.2, density=1.0))

        _obs, reward, terminated, truncated, info = env.step("local")

        self.assertEqual(info["finalized_tasks"], [])
        _obs1, reward1, terminated1, truncated1, info1 = env.step(None)
        self.assertEqual(info1["finalized_tasks"][0]["terminal_outcome"], "completed")
        self.assertEqual(info1["finalized_tasks"][0]["completion_slot"], 0)
        self.assertFalse(truncated)
        self.assertFalse(terminated)
        self.assertTrue(terminated1)
        self.assertFalse(truncated1)
        self.assertEqual(info1["metrics"]["completed"], 1.0)
        self.assertEqual(info1["metrics"]["dropped"], 0.0)
        self.assertEqual(reward, 0.0)
        self.assertLess(reward1, 0.0)

    def test_deterministic_same_slot_ordering_is_stable_across_repeated_runs(self) -> None:
        trace = EvaluationTrace(
            trace_id="deterministic-ordering",
            seed=106,
            tasks=(
                TraceTaskBlueprint(task_id=2, source_agent_id=1, arrival_slot=0, size=0.2, processing_density=1.0, timeout_length=5, absolute_deadline_slot=5),
                TraceTaskBlueprint(task_id=1, source_agent_id=1, arrival_slot=0, size=0.2, processing_density=1.0, timeout_length=5, absolute_deadline_slot=5),
            ),
            metadata={"mode": "deterministic_seed", "trace_id": "deterministic-ordering", "seed": "106"},
        )

        first_run = self._environment(trace)
        second_run = self._environment(trace)

        def run(env: HoodieGymEnvironment) -> list[int]:
            finalized_ids: list[int] = []
            while True:
                current_task = env.current_task
                action = "local" if current_task is not None else None
                _obs, _reward, terminated, truncated, info = env.step(action)
                finalized_ids.extend(task["task_id"] for task in info["finalized_tasks"])
                if terminated or truncated:
                    return finalized_ids

        self.assertEqual(run(first_run), [1, 2])
        self.assertEqual(run(second_run), [1, 2])


if __name__ == "__main__":
    unittest.main()
