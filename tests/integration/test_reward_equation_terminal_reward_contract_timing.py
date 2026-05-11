from __future__ import annotations

import unittest

from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.runtime_model import SharedRuntimeParameters
from src.evaluation.trace_protocol import EvaluationTrace, TraceTaskBlueprint


class RewardEquationTerminalRewardContractTimingIntegrationTest(unittest.TestCase):
    def _environment(self) -> HoodieGymEnvironment:
        trace = EvaluationTrace(
            trace_id="reward-contract-timing",
            seed=7,
            tasks=(
                TraceTaskBlueprint(task_id=1, source_agent_id=1, arrival_slot=0, size=1.0, processing_density=1.0, timeout_length=5, absolute_deadline_slot=5),
            ),
            metadata={"mode": "deterministic_seed", "trace_id": "reward-contract-timing", "seed": "7"},
        )
        env = HoodieGymEnvironment(
            episode_length=6,
            runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
            policy_name="HOODIE",
        )
        env.trace = trace
        env._pending_arrivals = {0: [trace.tasks[0]]}  # type: ignore[assignment]
        env.current_slot = 0
        env._current_task = env._load_current_task()
        return env

    def test_selected_action_does_not_emit_reward(self) -> None:
        env = self._environment()
        _obs, reward0, _terminated0, _truncated0, info0 = env.step("local")
        self.assertEqual(reward0, 0.0)
        self.assertNotIn("reward_emitted", info0["offload_lifecycle_events"])
        self.assertEqual(info0["finalized_tasks"], [])

    def test_reward_emitted_follows_terminal_completion_or_drop(self) -> None:
        env = self._environment()
        _obs, _reward0, _terminated0, _truncated0, _info0 = env.step("local")
        _obs, reward1, _terminated1, _truncated1, info1 = env.step(None)
        self.assertLess(reward1, 0.0)
        self.assertIn("execution_completed", info1["offload_lifecycle_events"])
        self.assertIn("reward_emitted", info1["offload_lifecycle_events"])

        drop_trace = EvaluationTrace(
            trace_id="reward-contract-drop",
            seed=8,
            tasks=(
                TraceTaskBlueprint(task_id=2, source_agent_id=1, arrival_slot=0, size=1.0, processing_density=1.0, timeout_length=0, absolute_deadline_slot=0),
            ),
            metadata={"mode": "deterministic_seed", "trace_id": "reward-contract-drop", "seed": "8"},
        )
        drop_env = HoodieGymEnvironment(
            episode_length=6,
            runtime_parameters=SharedRuntimeParameters(runtime_variant="constant_service"),
            policy_name="HOODIE",
        )
        drop_env.trace = drop_trace
        drop_env._pending_arrivals = {0: [drop_trace.tasks[0]]}  # type: ignore[assignment]
        drop_env.current_slot = 0
        drop_env._current_task = drop_env._load_current_task()
        _obs, _reward0, _terminated0, _truncated0, _info0 = drop_env.step("local")
        _obs, reward1, _terminated1, _truncated1, info1 = drop_env.step("local")
        self.assertLess(reward1, 0.0)
        self.assertIn("dropped_timeout", info1["offload_lifecycle_events"])
        self.assertIn("reward_emitted", info1["offload_lifecycle_events"])


if __name__ == "__main__":
    unittest.main()
