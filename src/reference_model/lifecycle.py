"""Deterministic lifecycle transition API for the reference kernel."""

from __future__ import annotations

from .ledger import LedgerEvent, LedgerEventType, TaskLedger
from .models import ActionInput, ActionType, TaskIdentity, TaskWorkload, TerminalStatus


class ReferenceLifecycleKernel:
    """Hand-fed deterministic lifecycle reference model."""

    def process(
        self,
        identity: TaskIdentity,
        workload: TaskWorkload,
        action: ActionInput,
    ) -> TaskLedger:
        if action.action_type is ActionType.LOCAL_COMPUTE:
            return self._local_compute(identity, workload, action)
        if action.action_type is ActionType.HORIZONTAL_OFFLOAD:
            return self._horizontal_offload(identity, workload, action)
        if action.action_type is ActionType.VERTICAL_OFFLOAD:
            return self._vertical_offload(identity, workload, action)
        raise ValueError(f"Unsupported action type: {action.action_type!r}")

    def _local_compute(
        self,
        identity: TaskIdentity,
        workload: TaskWorkload,
        action: ActionInput,
    ) -> TaskLedger:
        return self._build_ledger(
            identity,
            workload,
            [
                LedgerEvent(0, workload.current_slot, LedgerEventType.CREATED, identity.task_id),
                LedgerEvent(1, workload.current_slot, LedgerEventType.SELECTED_ACTION, identity.task_id),
                LedgerEvent(2, workload.current_slot, LedgerEventType.EXECUTION_STARTED, identity.task_id),
                LedgerEvent(3, workload.current_slot, LedgerEventType.EXECUTION_COMPLETED, identity.task_id, TerminalStatus.COMPLETED),
                LedgerEvent(4, workload.current_slot, LedgerEventType.REWARD_EMITTED, identity.task_id, TerminalStatus.COMPLETED),
            ],
            TerminalStatus.COMPLETED,
        )

    def _horizontal_offload(
        self,
        identity: TaskIdentity,
        workload: TaskWorkload,
        action: ActionInput,
    ) -> TaskLedger:
        return self._build_ledger(
            identity,
            workload,
            [
                LedgerEvent(0, workload.current_slot, LedgerEventType.CREATED, identity.task_id),
                LedgerEvent(1, workload.current_slot, LedgerEventType.SELECTED_ACTION, identity.task_id),
                LedgerEvent(2, workload.current_slot, LedgerEventType.QUEUED_PUBLIC, identity.task_id),
                LedgerEvent(3, workload.current_slot, LedgerEventType.TRANSMISSION_STARTED, identity.task_id),
                LedgerEvent(4, workload.current_slot, LedgerEventType.TRANSMISSION_COMPLETED, identity.task_id),
                LedgerEvent(5, workload.current_slot, LedgerEventType.EXECUTION_STARTED, identity.task_id),
                LedgerEvent(6, workload.current_slot, LedgerEventType.EXECUTION_COMPLETED, identity.task_id, TerminalStatus.COMPLETED),
                LedgerEvent(7, workload.current_slot, LedgerEventType.REWARD_EMITTED, identity.task_id, TerminalStatus.COMPLETED),
            ],
            TerminalStatus.COMPLETED,
        )

    def _vertical_offload(
        self,
        identity: TaskIdentity,
        workload: TaskWorkload,
        action: ActionInput,
    ) -> TaskLedger:
        return self._build_ledger(
            identity,
            workload,
            [
                LedgerEvent(0, workload.current_slot, LedgerEventType.CREATED, identity.task_id),
                LedgerEvent(1, workload.current_slot, LedgerEventType.SELECTED_ACTION, identity.task_id),
                LedgerEvent(2, workload.current_slot, LedgerEventType.OFFLOADED_CLOUD, identity.task_id),
                LedgerEvent(3, workload.current_slot, LedgerEventType.TRANSMISSION_STARTED, identity.task_id),
                LedgerEvent(4, workload.current_slot, LedgerEventType.TRANSMISSION_COMPLETED, identity.task_id),
                LedgerEvent(5, workload.current_slot, LedgerEventType.EXECUTION_STARTED, identity.task_id),
                LedgerEvent(6, workload.current_slot, LedgerEventType.EXECUTION_COMPLETED, identity.task_id, TerminalStatus.COMPLETED),
                LedgerEvent(7, workload.current_slot, LedgerEventType.REWARD_EMITTED, identity.task_id, TerminalStatus.COMPLETED),
            ],
            TerminalStatus.COMPLETED,
        )

    def process_timeout(
        self,
        identity: TaskIdentity,
        workload: TaskWorkload,
        action: ActionInput,
    ) -> TaskLedger:
        if workload.current_slot < workload.timeout_slot:
            raise ValueError("Timeout processing requires the current slot to reach the timeout boundary")
        return self._build_ledger(
            identity,
            workload,
            [
                LedgerEvent(0, workload.current_slot, LedgerEventType.CREATED, identity.task_id),
                LedgerEvent(1, workload.current_slot, LedgerEventType.SELECTED_ACTION, identity.task_id),
                LedgerEvent(2, workload.current_slot, LedgerEventType.DROPPED_TIMEOUT, identity.task_id, TerminalStatus.DROPPED_TIMEOUT),
                LedgerEvent(3, workload.current_slot, LedgerEventType.REWARD_EMITTED, identity.task_id, TerminalStatus.DROPPED_TIMEOUT),
            ],
            TerminalStatus.DROPPED_TIMEOUT,
        )

    def _build_ledger(
        self,
        identity: TaskIdentity,
        workload: TaskWorkload,
        events: list[LedgerEvent],
        terminal_status: TerminalStatus,
    ) -> TaskLedger:
        reward_emitted = any(event.event_type is LedgerEventType.REWARD_EMITTED for event in events)
        return TaskLedger.from_events(
            task_id=identity.task_id,
            events=events,
            terminal_status=terminal_status,
            reward_emitted=reward_emitted,
        )
