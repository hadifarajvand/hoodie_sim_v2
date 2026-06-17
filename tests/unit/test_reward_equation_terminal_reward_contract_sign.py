from __future__ import annotations

import math
import unittest

from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.runtime_model import SharedRuntimeParameters
from src.evaluation.trace_protocol import EvaluationTrace
from src.environment.task import Task


class RewardEquationTerminalRewardContractSignTest(unittest.TestCase):
    def test_reward_for_terminal_task_signs(self) -> None:
        from src.environment.reward_timing import reward_for_terminal_task

        completed = Task(
            task_id=1,
            source_agent_id=1,
            arrival_slot=0,
            size=1.0,
            processing_density=1.0,
            timeout_length=1,
            absolute_deadline_slot=3,
            completion_slot=3,
            terminal_outcome="completed",
            reward_emitted=True,
        )
        dropped = Task(
            task_id=2,
            source_agent_id=1,
            arrival_slot=0,
            size=1.0,
            processing_density=1.0,
            timeout_length=1,
            absolute_deadline_slot=1,
            terminal_outcome="dropped",
            reward_emitted=True,
        )

        self.assertEqual(reward_for_terminal_task(completed), -4.0)
        self.assertEqual(reward_for_terminal_task(dropped), -40.0)

    def test_no_task_slot_emits_nan_reward_and_does_not_pollute_metrics(self) -> None:
        env = HoodieGymEnvironment(
            episode_length=1,
            runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
            policy_name="HOODIE",
        )
        env.reset(seed=11)
        env.trace = EvaluationTrace(trace_id="idle", seed=11, tasks=(), metadata={"mode": "deterministic_seed"})
        env._pending_arrivals = {}  # type: ignore[assignment]
        env._current_task = None

        _obs, reward, _terminated, _truncated, info = env.step(None)
        self.assertTrue(math.isnan(reward))
        self.assertEqual(info["metrics"]["reward"], 0.0)


if __name__ == "__main__":
    unittest.main()
