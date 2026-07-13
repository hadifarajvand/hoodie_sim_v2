from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
import random
from typing import Deque, Iterable


@dataclass(slots=True)
class Transition:
    state: dict[str, object]
    action: str
    reward: float
    next_state: dict[str, object]
    done: bool
    delta_slots: int = 1


@dataclass(slots=True)
class ReplayBuffer:
    capacity: int = 10_000
    seed: int = 0
    _items: Deque[Transition] = field(default_factory=deque)
    _rng: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    def add(self, transition: Transition) -> None:
        self._items.append(transition)
        while len(self._items) > self.capacity:
            self._items.popleft()

    def extend(self, transitions: Iterable[Transition]) -> None:
        for transition in transitions:
            self.add(transition)

    def reseed(self, seed: int) -> None:
        self.seed = seed
        self._rng = random.Random(seed)

    def sample(self, batch_size: int) -> tuple[Transition, ...]:
        batch_size = min(batch_size, len(self._items))
        if batch_size <= 0:
            return ()
        indices = sorted(self._rng.sample(range(len(self._items)), batch_size))
        items = list(self._items)
        return tuple(items[index] for index in indices)

    def __len__(self) -> int:
        return len(self._items)
