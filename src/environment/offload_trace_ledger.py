from __future__ import annotations

from dataclasses import dataclass, field

from .offload_trace_schema import OFFLOAD_LIFECYCLE_EVENTS


@dataclass(slots=True)
class OffloadTraceLedger:
    event_sequence: list[str] = field(default_factory=list)

    def emit(self, event: str) -> None:
        if event not in OFFLOAD_LIFECYCLE_EVENTS:
            raise ValueError(f"Unsupported offload lifecycle event: {event}")
        self.event_sequence.append(event)

    def extend(self, events: list[str]) -> None:
        for event in events:
            self.emit(event)

    def snapshot(self) -> tuple[str, ...]:
        return tuple(self.event_sequence)

