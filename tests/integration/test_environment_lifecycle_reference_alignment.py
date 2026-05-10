from __future__ import annotations

import unittest

from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.runtime_model import SharedRuntimeParameters
from src.evaluation.trace_protocol import EvaluationTrace, TraceTaskBlueprint
from src.reference_model import ActionInput, ActionType, ReferenceLifecycleKernel, TaskIdentity, TaskWorkload


class EnvironmentLifecycleReferenceAlignmentIntegrationTest(unittest.TestCase):
    def _environment(self) -> HoodieGymEnvironment:
        trace = EvaluationTrace(
            trace_id="reference-alignment",
            seed=201,
            tasks=(
                TraceTaskBlueprint(
                    task_id=1,
                    source_agent_id=1,
                    arrival_slot=0,
                    size=64.0,
                    processing_density=2.0,
                    timeout_length=5,
                    absolute_deadline_slot=5,
                ),
            ),
            metadata={"mode": "deterministic_seed", "trace_id": "reference-alignment", "seed": "201"},
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

    def test_local_compute_terminal_status_matches_reference_kernel(self) -> None:
        env = self._environment()
        kernel = ReferenceLifecycleKernel()
        identity = TaskIdentity(task_id="1", origin_edge_agent="1", destination_target="1")
        workload = TaskWorkload(task_size=64, timeout_slot=5, current_slot=0)
        reference_ledger = kernel.process(identity, workload, ActionInput(ActionType.LOCAL_COMPUTE, destination_target="1"))

        _obs, _reward, _terminated, _truncated, info = env.step("local")

        self.assertEqual(reference_ledger.terminal_status.value, info["finalized_tasks"][0]["terminal_outcome"])
        self.assertEqual(reference_ledger.reward_emitted, True)
        self.assertEqual(info["finalized_tasks"][0]["completion_slot"], 0)


if __name__ == "__main__":
    unittest.main()
