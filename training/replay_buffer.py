from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class Transition:
    state: np.ndarray
    action: int
    reward: float
    next_state: np.ndarray
    done: bool
    task_id: int | None = None
    step_index: int | None = None
    policy_name: str | None = None

    def validate(self) -> None:
        if self.state.shape != self.next_state.shape:
            raise ValueError("state and next_state must have identical shapes")
        if self.state.ndim != 1:
            raise ValueError("state must be a 1D vector")
        if not isinstance(self.action, int):
            raise TypeError("action must be an int")


class ReplayBuffer:
    def __init__(self, capacity: int, seed: int | None = None) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self._buffer: list[Transition] = []
        self._position = 0
        self._rng = np.random.default_rng(seed)

    def __len__(self) -> int:
        return len(self._buffer)

    def push(self, transition: Transition) -> None:
        transition.validate()
        if len(self._buffer) < self.capacity:
            self._buffer.append(transition)
        else:
            self._buffer[self._position] = transition
        self._position = (self._position + 1) % self.capacity

    def sample(self, batch_size: int) -> list[Transition]:
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if batch_size > len(self._buffer):
            raise ValueError("batch_size exceeds buffer length")
        indices = self._rng.choice(len(self._buffer), size=batch_size, replace=False)
        return [self._buffer[int(index)] for index in indices]

    def clear(self) -> None:
        self._buffer.clear()
        self._position = 0

    def to_list(self) -> list[Transition]:
        return list(self._buffer)
