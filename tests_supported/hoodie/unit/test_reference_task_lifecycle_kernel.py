from __future__ import annotations

import unittest

from src.reference_model import (
    ActionInput,
    ActionType,
    LedgerEventType,
    ReferenceLifecycleKernel,
    TaskIdentity,
    TaskWorkload,
    TerminalStatus,
)


class ReferenceTaskLifecycleKernelTest(unittest.TestCase):
    def setUp(self) -> None:
        self.kernel = ReferenceLifecycleKernel()
        self.identity = TaskIdentity(
            task_id="task-1",
            origin_edge_agent="ea-1",
            destination_target="ea-2",
        )

    def test_local_compute_ledger(self) -> None:
        ledger = self.kernel.process(
            self.identity,
            TaskWorkload(task_size=10, timeout_slot=5, current_slot=2),
            ActionInput(ActionType.LOCAL_COMPUTE, destination_target="ea-1"),
        )
        self.assertEqual(
            ledger.event_types(),
            (
                LedgerEventType.CREATED,
                LedgerEventType.SELECTED_ACTION,
                LedgerEventType.EXECUTION_STARTED,
                LedgerEventType.EXECUTION_COMPLETED,
                LedgerEventType.REWARD_EMITTED,
            ),
        )
        self.assertTrue(ledger.reward_emitted)

    def test_local_compute_is_deterministic(self) -> None:
        workload = TaskWorkload(task_size=10, timeout_slot=5, current_slot=2)
        action = ActionInput(ActionType.LOCAL_COMPUTE, destination_target="ea-1")
        first = self.kernel.process(self.identity, workload, action)
        second = self.kernel.process(self.identity, workload, action)
        self.assertEqual(first, second)

    def test_horizontal_offload_ledger(self) -> None:
        ledger = self.kernel.process(
            self.identity,
            TaskWorkload(task_size=10, timeout_slot=5, current_slot=2),
            ActionInput(ActionType.HORIZONTAL_OFFLOAD, destination_target="ea-2"),
        )
        self.assertEqual(
            ledger.event_types(),
            (
                LedgerEventType.CREATED,
                LedgerEventType.SELECTED_ACTION,
                LedgerEventType.QUEUED_PUBLIC,
                LedgerEventType.TRANSMISSION_STARTED,
                LedgerEventType.TRANSMISSION_COMPLETED,
                LedgerEventType.EXECUTION_STARTED,
                LedgerEventType.EXECUTION_COMPLETED,
                LedgerEventType.REWARD_EMITTED,
            ),
        )

    def test_vertical_offload_ledger(self) -> None:
        ledger = self.kernel.process(
            self.identity,
            TaskWorkload(task_size=10, timeout_slot=5, current_slot=2),
            ActionInput(ActionType.VERTICAL_OFFLOAD, destination_target="cloud"),
        )
        self.assertEqual(
            ledger.event_types(),
            (
                LedgerEventType.CREATED,
                LedgerEventType.SELECTED_ACTION,
                LedgerEventType.OFFLOADED_CLOUD,
                LedgerEventType.TRANSMISSION_STARTED,
                LedgerEventType.TRANSMISSION_COMPLETED,
                LedgerEventType.EXECUTION_STARTED,
                LedgerEventType.EXECUTION_COMPLETED,
                LedgerEventType.REWARD_EMITTED,
            ),
        )

    def test_timeout_drop_ledger(self) -> None:
        ledger = self.kernel.process_timeout(
            self.identity,
            TaskWorkload(task_size=10, timeout_slot=2, current_slot=2),
            ActionInput(ActionType.LOCAL_COMPUTE, destination_target="ea-1"),
        )
        self.assertEqual(
            ledger.event_types(),
            (
                LedgerEventType.CREATED,
                LedgerEventType.SELECTED_ACTION,
                LedgerEventType.DROPPED_TIMEOUT,
                LedgerEventType.REWARD_EMITTED,
            ),
        )
        self.assertTrue(ledger.reward_emitted)
        self.assertEqual(ledger.terminal_status, TerminalStatus.DROPPED_TIMEOUT)

    def test_reward_not_emitted_at_selection(self) -> None:
        ledger = self.kernel.process(
            self.identity,
            TaskWorkload(task_size=10, timeout_slot=5, current_slot=2),
            ActionInput(ActionType.LOCAL_COMPUTE, destination_target="ea-1"),
        )
        selected_index = ledger.event_types().index(LedgerEventType.SELECTED_ACTION)
        reward_index = ledger.event_types().index(LedgerEventType.REWARD_EMITTED)
        self.assertGreater(reward_index, selected_index)


if __name__ == "__main__":
    unittest.main()
