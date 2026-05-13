from __future__ import annotations

import unittest

from src.environment.environment import finalize_task_runtime_state_with_parameters
from src.environment.runtime_model import SharedRuntimeParameters
from src.environment.task import Task
from src.analysis.deadline_timeout_off_by_one_audit import build_deadline_timeout_off_by_one_audit_report


class DeadlineTimeoutOffByOneAuditIntegrationTests(unittest.TestCase):
    def _task(self, *, arrival_slot: int = 0, absolute_deadline_slot: int = 20) -> Task:
        timeout_length = absolute_deadline_slot - arrival_slot
        return Task(
            task_id=1,
            source_agent_id=1,
            arrival_slot=arrival_slot,
            size=1.0,
            processing_density=1.0,
            timeout_length=timeout_length,
            absolute_deadline_slot=absolute_deadline_slot,
        )

    def test_environment_exact_deadline_completion_not_dropped(self) -> None:
        task = self._task()
        task.completion_slot = 20
        finalize_task_runtime_state_with_parameters(task, current_slot=20, parameters=SharedRuntimeParameters())

        self.assertEqual(task.terminal_outcome, "completed")
        self.assertFalse(task.drop_flag)

    def test_reward_emitted_only_after_terminal_completion_drop(self) -> None:
        task = self._task()
        task.completion_slot = 20
        finalize_task_runtime_state_with_parameters(task, current_slot=20, parameters=SharedRuntimeParameters())
        self.assertTrue(task.reward_emitted)

    def test_drop_penalty_only_after_deadline_drop(self) -> None:
        task = self._task()
        task.completion_slot = 21
        finalize_task_runtime_state_with_parameters(task, current_slot=21, parameters=SharedRuntimeParameters())
        self.assertEqual(task.terminal_outcome, "dropped")
        self.assertTrue(task.drop_flag)

    def test_report_builder_exposes_feature_036_contract(self) -> None:
        report = build_deadline_timeout_off_by_one_audit_report()
        self.assertEqual(report.feature_id, "036-deadline-timeout-off-by-one-audit")
        self.assertTrue(report.contradiction_detected)
        self.assertIn("src/environment/deadline_rules.py", report.repaired_runtime_components)
        self.assertIn("current_slot == absolute_deadline_slot -> not expired", report.boundary_cases_validated)


if __name__ == "__main__":
    unittest.main()
