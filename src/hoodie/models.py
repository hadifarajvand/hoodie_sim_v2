from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Mapping


@dataclass(frozen=True, slots=True)
class Identifier:
    value: str


@dataclass(frozen=True, slots=True)
class Time:
    slot: int


@dataclass(frozen=True, slots=True)
class Unit:
    value: float
    label: str


@dataclass(frozen=True, slots=True)
class Action:
    name: str
    destination: str | None = None


@dataclass(frozen=True, slots=True)
class Outcome:
    name: str
    terminal: bool = False
    dropped: bool = False


@dataclass(frozen=True, slots=True)
class Task:
    task_id: Identifier
    source_id: Identifier
    arrival: Time
    size: Unit
    density: Unit
    timeout_slots: int


@dataclass(frozen=True, slots=True)
class Trace:
    events: tuple[Mapping[str, object], ...]

    def hash(self) -> str:
        payload = str(tuple(sorted(tuple(sorted(event.items())) for event in self.events))).encode("utf-8")
        return sha256(payload).hexdigest()
