from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from hashlib import sha256
from typing import Iterable

from .models import Action, Outcome, Task, Trace
from .topology import Topology


@dataclass
class FIFOQueue:
    items: deque[Task] = field(default_factory=deque)

    def push(self, task: Task) -> None:
        self.items.append(task)

    def pop(self) -> Task:
        return self.items.popleft()

    def __len__(self) -> int:
        return len(self.items)


@dataclass(frozen=True, slots=True)
class ServiceResult:
    service_slots: int
    outcome: Outcome


class NeutralSlotKernel:
    def step(self, task: Task, action: Action, *, current_slot: int) -> Outcome:
        timeout_slot = task.arrival.slot + task.timeout_slots
        if current_slot >= timeout_slot:
            return Outcome(name="dropped", terminal=True, dropped=True)
        if action.name == "drop":
            return Outcome(name="dropped", terminal=True, dropped=True)
        return Outcome(name="completed", terminal=True, dropped=False)


@dataclass
class HoodieKernel:
    topology: Topology
    local_capacity: float = 1.0
    horizontal_capacity: float = 1.0
    vertical_capacity: float = 1.0

    def legal_actions(self, source_id: str) -> tuple[str, ...]:
        return self.topology.legal_actions.get(source_id, ())

    def service_time(self, task: Task, action: Action) -> ServiceResult:
        if action.name == "local":
            service = max(1, int(task.size.value / self.local_capacity))
        elif action.name == "horizontal":
            service = max(1, int(task.size.value / self.horizontal_capacity))
        elif action.name == "vertical":
            service = max(1, int(task.size.value / self.vertical_capacity))
        else:
            service = 1
        return ServiceResult(service_slots=service, outcome=Outcome(name="pending"))

    def trace_hash(self, trace: Trace) -> str:
        return trace.hash()


def hash_events(events: Iterable[dict[str, object]]) -> str:
    payload = repr(tuple(tuple(sorted(event.items())) for event in events)).encode("utf-8")
    return sha256(payload).hexdigest()
