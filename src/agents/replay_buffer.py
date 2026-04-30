from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Iterable


@dataclass(slots=True)
class Transition:
    state: dict[str, object]
    action: str
    reward: float
    next_state: dict[str, object]
    done: bool


@dataclass(slots=True)
class ReplayBuffer:
    capacity: int = 10_000
    _items: Deque[Transition] = field(default_factory=deque)

    def add(self, transition: Transition) -> None:
        self._items.append(transition)
        while len(self._items) > self.capacity:
            self._items.popleft()

    def extend(self, transitions: Iterable[Transition]) -> None:
        for transition in transitions:
            self.add(transition)

    def sample(self, batch_size: int) -> tuple[Transition, ...]:
        batch_size = min(batch_size, len(self._items))
        return tuple(list(self._items)[-batch_size:])

    def __len__(self) -> int:
        return len(self._items)
