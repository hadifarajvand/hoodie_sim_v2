from __future__ import annotations

import unittest

from src.environment.deadline_rules import has_expired
from src.environment.environment import finalize_task_runtime_state_with_parameters
from src.environment.runtime_model import SharedRuntimeParameters, resolve_runtime_terminal_state
from src.environment.task import Task
from src.environment.traffic_config import TrafficScenarioPreset


class TimeoutBoundaryContractTests(unittest.TestCase):
    def _task(self, arrival_slot: int = 0, absolute_deadline_slot: int = 20) -> Task:
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

    def test_paper_default_timeout_contract_20_slots_2_seconds(self) -> None:
        config = TrafficScenarioPreset.paper_default()

        self.assertEqual(config.timeout_slots, 20)
        self.assertEqual(config.slot_duration_seconds, 0.1)
        self.assertEqual(TrafficScenarioPreset.timeout_seconds(config), 2.0)

    def test_completion_before_deadline_is_completed(self) -> None:
        task = self._task()
        self.assertFalse(has_expired(task, current_slot=19))

    def test_completion_exactly_at_deadline_is_completed(self) -> None:
        task = self._task()
        self.assertFalse(has_expired(task, current_slot=20))

    def test_completion_after_deadline_is_dropped(self) -> None:
        task = self._task()
        self.assertTrue(has_expired(task, current_slot=21))

    def test_nonzero_arrival_exact_deadline_boundary(self) -> None:
        task = self._task(arrival_slot=5, absolute_deadline_slot=25)
        self.assertFalse(has_expired(task, current_slot=25))

    def test_deadline_rules_boundary_matches_timeout_contract(self) -> None:
        task = self._task()
        self.assertFalse(has_expired(task, current_slot=20))
        self.assertTrue(has_expired(task, current_slot=21))

    def test_runtime_model_boundary_matches_environment_contract(self) -> None:
        task = self._task()
        resolve_runtime_terminal_state(task, terminal_slot=20, current_slot=20, parameters=SharedRuntimeParameters())
        self.assertEqual(task.terminal_outcome, "completed")

        late = self._task()
        resolve_runtime_terminal_state(late, terminal_slot=21, current_slot=21, parameters=SharedRuntimeParameters())
        self.assertEqual(late.terminal_outcome, "dropped")

    def test_environment_finalize_task_runtime_state_boundary_matches_contract(self) -> None:
        task = self._task()
        task.completion_slot = 20
        finalize_task_runtime_state_with_parameters(task, current_slot=20, parameters=SharedRuntimeParameters())
        self.assertEqual(task.terminal_outcome, "completed")
        self.assertFalse(task.drop_flag)
        self.assertTrue(task.reward_emitted)


if __name__ == "__main__":
    unittest.main()
