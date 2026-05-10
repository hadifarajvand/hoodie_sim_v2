"""Deterministic ledger primitives for the reference lifecycle kernel."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Sequence

from .models import TerminalStatus


class LedgerEventType(str, Enum):
    CREATED = "created"
    SELECTED_ACTION = "selected_action"
    QUEUED_PRIVATE = "queued_private"
    QUEUED_PUBLIC = "queued_public"
    OFFLOADED_CLOUD = "offloaded_cloud"
    TRANSMISSION_STARTED = "transmission_started"
    TRANSMISSION_COMPLETED = "transmission_completed"
    EXECUTION_STARTED = "execution_started"
    EXECUTION_COMPLETED = "execution_completed"
    DROPPED_TIMEOUT = "dropped_timeout"
    REWARD_EMITTED = "reward_emitted"


@dataclass(frozen=True, slots=True)
class LedgerEvent:
    sequence_index: int
    slot: int
    event_type: LedgerEventType
    task_id: str
    status: TerminalStatus | None = None
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class TaskLedger:
    task_id: str
    events: tuple[LedgerEvent, ...] = field(default_factory=tuple)
    terminal_status: TerminalStatus | None = None
    reward_emitted: bool = False

    def event_types(self) -> tuple[LedgerEventType, ...]:
        return tuple(event.event_type for event in self.events)

    @classmethod
    def from_events(
        cls,
        task_id: str,
        events: Sequence[LedgerEvent],
        terminal_status: TerminalStatus | None,
        reward_emitted: bool,
    ) -> "TaskLedger":
        ordered = tuple(sorted(events, key=_ledger_sort_key))
        _validate_sequence_order(ordered)
        return cls(
            task_id=task_id,
            events=ordered,
            terminal_status=terminal_status,
            reward_emitted=reward_emitted,
        )


_EVENT_PRIORITY = {
    LedgerEventType.CREATED: 0,
    LedgerEventType.SELECTED_ACTION: 1,
    LedgerEventType.QUEUED_PRIVATE: 2,
    LedgerEventType.QUEUED_PUBLIC: 2,
    LedgerEventType.OFFLOADED_CLOUD: 2,
    LedgerEventType.TRANSMISSION_STARTED: 3,
    LedgerEventType.TRANSMISSION_COMPLETED: 4,
    LedgerEventType.EXECUTION_STARTED: 5,
    LedgerEventType.EXECUTION_COMPLETED: 6,
    LedgerEventType.DROPPED_TIMEOUT: 6,
    LedgerEventType.REWARD_EMITTED: 7,
}


def _ledger_sort_key(event: LedgerEvent) -> tuple[int, int, int, str]:
    return (
        event.slot,
        _EVENT_PRIORITY[event.event_type],
        event.sequence_index,
        event.event_type.value,
    )


def _validate_sequence_order(events: Iterable[LedgerEvent]) -> None:
    previous_index = -1
    for event in events:
        if event.sequence_index <= previous_index:
            raise ValueError("Ledger event sequence_index must be strictly increasing")
        previous_index = event.sequence_index

