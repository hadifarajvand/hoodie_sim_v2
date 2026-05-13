from __future__ import annotations

import unittest

from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.runtime_model import SharedRuntimeParameters
from src.evaluation.trace_protocol import EvaluationTrace, TraceTaskBlueprint
from src.policies.flc import FullLocalComputingPolicy
from src.policies.policy_interface import PolicyContext


class _TestLocalLearnedPolicyStub:
    def choose_action(self, context: PolicyContext) -> str:
        return "local"


class MechanismRepairTimeoutDropIntegrationTest(unittest.TestCase):
    def _timeout_trace(self, *, task_id: int = 1, timeout_slot: int = 1) -> EvaluationTrace:
        return EvaluationTrace(
            trace_id=f"timeout-drop-{task_id}",
            seed=104,
            tasks=(
                TraceTaskBlueprint(
                    task_id=task_id,
                    source_agent_id=1,
                    arrival_slot=0,
                    size=1.0,
                    processing_density=1.0,
                    timeout_length=timeout_slot,
                    absolute_deadline_slot=timeout_slot,
                ),
            ),
            metadata={"mode": "deterministic_seed", "trace_id": f"timeout-drop-{task_id}", "seed": "104"},
        )

    def _environment(self, trace: EvaluationTrace) -> HoodieGymEnvironment:
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

    def _run_policy_episode(self, env: HoodieGymEnvironment, policy: object) -> list[tuple]:
        observation, _info = env.observe(), env._build_info()
        sequence: list[tuple] = []
        while True:
            current_task = env.current_task
            if current_task is None:
                action = None
            else:
                action = policy.choose_action(
                    PolicyContext(
                        observation=env.observe_flat(current_task),
                        legal_action_mask=env.legal_action_mask(current_task),
                        trace_history=(env.trace.trace_id if env.trace is not None else "",),
                    )
                )
            observation, reward, terminated, truncated, info = env.step(action)
            finalized = tuple((task["task_id"], task["terminal_outcome"]) for task in info["finalized_tasks"])
            sequence.append((reward, terminated, truncated, finalized, info["slot"]))
            if terminated or truncated:
                return sequence

    def test_baseline_policy_path_runs_through_public_environment_interface(self) -> None:
        env = self._environment(self._timeout_trace(task_id=11, timeout_slot=5))
        policy = FullLocalComputingPolicy()

        sequence = self._run_policy_episode(env, policy)

        self.assertTrue(sequence)
        self.assertTrue(any(finalized for _reward, _terminated, _truncated, finalized, _slot in sequence))
        self.assertTrue(all(isinstance(step[0], float) for step in sequence))

    def test_learned_policy_placeholder_stub_runs_through_public_environment_interface(self) -> None:
        env = self._environment(self._timeout_trace(task_id=12, timeout_slot=5))
        policy = _TestLocalLearnedPolicyStub()

        sequence = self._run_policy_episode(env, policy)

        self.assertTrue(sequence)
        self.assertTrue(any(finalized for _reward, _terminated, _truncated, finalized, _slot in sequence))
        self.assertEqual(sequence[-1][1] or sequence[-1][2], True)

    def test_timeout_drop_repair_uses_public_step_lifecycle(self) -> None:
        env = self._environment(self._timeout_trace(task_id=13, timeout_slot=1))

        _obs0, _reward0, _terminated0, _truncated0, _info0 = env.step("local")
        _obs1, reward1, _terminated1, _truncated1, info1 = env.step(None)

        self.assertEqual(info1["finalized_tasks"][0]["terminal_outcome"], "completed")
        self.assertIn("reward_emitted", info1["finalized_tasks"][0]["offload_lifecycle_events"])
        self.assertTrue(info1["terminated"])
        self.assertFalse(info1["truncated"])


if __name__ == "__main__":
    unittest.main()
