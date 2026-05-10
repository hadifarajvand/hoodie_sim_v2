from __future__ import annotations

import unittest

from src.audits.differential_environment import ComparisonClassification, FindingCause, DifferentialEnvironmentAudit, build_default_toy_cases
from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.runtime_model import SharedRuntimeParameters
from src.evaluation.trace_protocol import EvaluationTrace, TraceTaskBlueprint
from src.reference_model import ActionInput, ActionType, ReferenceLifecycleKernel, TaskIdentity, TaskWorkload


class EnvironmentLifecycleRepairFlowIntegrationTest(unittest.TestCase):
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

    def test_local_compute_environment_matches_reference_terminal_status(self) -> None:
        trace = EvaluationTrace(
            trace_id="repair-local",
            seed=101,
            tasks=(
                TraceTaskBlueprint(
                    task_id=1,
                    source_agent_id=1,
                    arrival_slot=0,
                    size=84.0,
                    processing_density=2.0,
                    timeout_length=5,
                    absolute_deadline_slot=5,
                ),
            ),
            metadata={"mode": "deterministic_seed", "trace_id": "repair-local", "seed": "101"},
        )
        env = self._environment(trace)
        kernel = ReferenceLifecycleKernel()
        identity = TaskIdentity(task_id="1", origin_edge_agent="1", destination_target="1")
        workload = TaskWorkload(task_size=84, timeout_slot=5, current_slot=0)
        reference_ledger = kernel.process(identity, workload, ActionInput(ActionType.LOCAL_COMPUTE, destination_target="1"))

        _obs, _reward, terminated, truncated, info = env.step("local")

        self.assertEqual(reference_ledger.terminal_status.value, "completed")
        self.assertEqual(info["finalized_tasks"][0]["terminal_outcome"], "completed")
        self.assertTrue(terminated)
        self.assertFalse(truncated)

    def test_regenerated_differential_audit_no_longer_reports_likely_environment_bug(self) -> None:
        report = DifferentialEnvironmentAudit().run(build_default_toy_cases())
        payload = report.to_dict()
        results = {item["case_id"]: item for item in payload["comparison_results"]}
        self.assertEqual(results["case-local-compute"]["classification"], ComparisonClassification.MATCH.value)
        self.assertEqual(results["case-deterministic-ordering"]["classification"], ComparisonClassification.MATCH.value)
        self.assertNotEqual(results["case-local-compute"]["finding_cause"], FindingCause.LIKELY_ENVIRONMENT_BUG.value)
        self.assertNotEqual(results["case-deterministic-ordering"]["finding_cause"], FindingCause.LIKELY_ENVIRONMENT_BUG.value)


if __name__ == "__main__":
    unittest.main()
