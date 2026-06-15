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
    episode_id: int | None = None
    task_id: int | None = None
    step_index: int | None = None
    policy_name: str | None = None
    raw_action_id: int | None = None
    first_stage_decision: str | None = None
    destination_node_id: int | None = None
    destination_type: str | None = None
    is_valid: bool | None = None
    invalid_reason: str | None = None
    adjacency_allowed: bool | None = None
    cloud_target: bool | None = None
    d_n_1: int | None = None
    d_nk_2: dict[int, int] | None = None
    eta_n: float | None = None
    w_priv_n: float | None = None
    w_off_n: float | None = None
    l_pub_n_prev: np.ndarray | None = None
    load_history: np.ndarray | None = None
    predicted_next_load: np.ndarray | None = None
    active_load_vector: np.ndarray | None = None
    reward_source: str | None = None
    reward_reason: str | None = None
    reward_timing_convention: str | None = None
    paired_transition_found: bool | None = None
    replay_pairing_status: str | None = None
    state_source: str | None = None
    next_state_source: str | None = None

    def validate(self) -> None:
        if self.state.shape != self.next_state.shape:
            raise ValueError("state and next_state must have identical shapes")
        if self.state.ndim != 1:
            raise ValueError("state must be a 1D vector")
        if self.next_state.ndim != 1:
            raise ValueError("next_state must be a 1D vector")
        if not isinstance(self.action, int):
            raise TypeError("action must be an int")
        if not isinstance(self.done, bool):
            raise TypeError("done must be a bool")
        if not np.all(np.isfinite(self.state)):
            raise ValueError("state must contain only finite values")
        if not np.all(np.isfinite(self.next_state)):
            raise ValueError("next_state must contain only finite values")
        if not np.isfinite(self.reward):
            raise ValueError("reward must be finite")
        for field_name in ("l_pub_n_prev", "load_history", "active_load_vector", "predicted_next_load"):
            value = getattr(self, field_name)
            if value is None:
                continue
            array = np.asarray(value)
            if not np.all(np.isfinite(array)):
                raise ValueError(f"{field_name} must contain only finite values")


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

    def sample_indices(self, batch_size: int) -> np.ndarray:
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if batch_size > len(self._buffer):
            raise ValueError("batch_size exceeds buffer length")
        return self._rng.choice(len(self._buffer), size=batch_size, replace=False)

    def clear(self) -> None:
        self._buffer.clear()
        self._position = 0

    def to_list(self) -> list[Transition]:
        return list(self._buffer)
