from __future__ import annotations

import unittest

from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.runtime_model import SharedRuntimeParameters
from src.evaluation.trace_protocol import EvaluationTrace, TraceTaskBlueprint


class MechanismRepairTimeoutDropUnitTest(unittest.TestCase):
    def _timeout_trace(self, *, task_id: int = 1, timeout_slot: int = 1) -> EvaluationTrace:
        return EvaluationTrace(
            trace_id=f"timeout-drop-{task_id}",
            seed=104,
            tasks=(
                TraceTaskBlueprint(
                    task_id=task_id,
                    source_agent_id=1,
                    arrival_slot=0,
                    size=32.0,
                    processing_density=1.0,
                    timeout_length=timeout_slot,
                    absolute_deadline_slot=timeout_slot,
                ),
            ),
            metadata={"mode": "deterministic_seed", "trace_id": f"timeout-drop-{task_id}", "seed": "104"},
        )

    def _environment(self, trace: EvaluationTrace, *, runtime_variant: str = "constant_service") -> HoodieGymEnvironment:
        env = HoodieGymEnvironment(
            episode_length=6,
            runtime_parameters=SharedRuntimeParameters(runtime_variant=runtime_variant),
            policy_name="HOODIE",
        )
        env.trace = trace
        env._pending_arrivals = {0: [trace.tasks[0]]}  # type: ignore[assignment]
        env.current_slot = 0
        env._current_task = env._load_current_task()
        return env

    def test_timeout_boundary_drops_in_public_environment_step(self) -> None:
        trace = self._timeout_trace(timeout_slot=1)
        env = self._environment(trace)

        _obs0, reward0, terminated0, truncated0, info0 = env.step("local")
        _obs1, reward1, terminated1, truncated1, info1 = env.step(None)

        self.assertEqual(info1["finalized_tasks"][0]["terminal_outcome"], "dropped")
        self.assertEqual(info1["finalized_tasks"][0]["completion_slot"], 1)
        self.assertEqual(reward0, 0.0)
        self.assertLess(reward1, 0.0)
        self.assertFalse(terminated0)
        self.assertFalse(truncated0)
        self.assertTrue(terminated1)
        self.assertFalse(truncated1)
        self.assertTrue(info1["terminated"])
        self.assertFalse(info1["truncated"])
        self.assertEqual(info1["metrics"]["dropped"], 1.0)
        self.assertEqual(info1["metrics"]["completed"], 0.0)

    def test_local_completion_still_works_for_non_timeout_case(self) -> None:
        trace = self._timeout_trace(task_id=2, timeout_slot=5)
        env = self._environment(trace)

        _obs0, reward0, _terminated0, _truncated0, _info0 = env.step("local")
        _obs1, reward1, terminated1, truncated1, info1 = env.step(None)

        self.assertEqual(info1["finalized_tasks"][0]["terminal_outcome"], "completed")
        self.assertLess(reward1, 0.0)
        self.assertEqual(info1["metrics"]["completed"], 1.0)
        self.assertEqual(info1["metrics"]["dropped"], 0.0)
        self.assertTrue(terminated1 or truncated1 or info1["terminated"] or info1["truncated"])


if __name__ == "__main__":
    unittest.main()
