from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any, Iterable

import torch

ACTION_INDEX_TO_SEMANTICS: dict[int, str] = {
    0: "local",
    1: "horizontal",
    2: "vertical",
}

LOOKBACK_W = 10
DATA_SOURCE = "paper_default_terminal_exposure_probe"


def zero_state_row() -> tuple[float, float, float]:
    return (0.0, 0.0, 0.0)


def build_state_window(history: Iterable[tuple[float, float, float]]) -> tuple[tuple[float, float, float], ...]:
    rows = list(history)[-LOOKBACK_W:]
    if len(rows) < LOOKBACK_W:
        rows = [zero_state_row() for _ in range(LOOKBACK_W - len(rows))] + rows
    return tuple(rows)


def build_state_window_tensor(window: tuple[tuple[float, float, float], ...], *, device: torch.device | None = None) -> torch.Tensor:
    return torch.tensor(window, dtype=torch.float32, device=device)


def build_state_vector(*, observation: dict[str, Any], current_task: Any | None, episode_length: int) -> tuple[float, float, float]:
    slot = float(observation.get("slot", 0.0))
    queue_load = float(observation.get("queue_load", 0.0))
    history_length = float(observation.get("history_length", 0.0))
    slot_norm = slot / max(float(episode_length - 1), 1.0)
    queue_norm = min(queue_load / max(float(episode_length), 1.0), 1.0)
    history_norm = min(history_length / max(float(episode_length), 1.0), 1.0)
    if current_task is None:
        return (slot_norm, queue_norm, history_norm)
    size_norm = min(float(getattr(current_task, "size", 0.0)) / 100.0, 1.0)
    density_norm = min(float(getattr(current_task, "processing_density", 0.0)) / 5.0, 1.0)
    return (slot_norm, size_norm, density_norm)


def legal_action_mask_to_tuple(mask: dict[str, bool]) -> tuple[bool, bool, bool]:
    return (bool(mask.get("local", False)), bool(mask.get("horizontal", False)), bool(mask.get("vertical", False)))


@dataclass(slots=True, frozen=True)
class ReplayTransition:
    state: tuple[tuple[float, float, float], ...]
    action: int
    legal_action_mask: tuple[bool, bool, bool]
    next_state: tuple[tuple[float, float, float], ...]
    reward: float
    reward_available: bool
    terminal: bool
    terminal_reason: str | None
    pending_at_horizon: bool
    arrival_slot: int
    completion_or_drop_slot: int | None
    agent_id: int
    episode_id: int
    step_id: int
    source_type: str = DATA_SOURCE

    def __post_init__(self) -> None:
        if len(self.state) != LOOKBACK_W or len(self.next_state) != LOOKBACK_W:
            raise ValueError("ReplayTransition.state and next_state must contain ten history rows.")
        if self.action not in ACTION_INDEX_TO_SEMANTICS:
            raise ValueError("ReplayTransition.action must be one of the stable action indices 0, 1, or 2.")
        if len(self.legal_action_mask) != 3:
            raise ValueError("ReplayTransition.legal_action_mask must contain three entries.")
        if self.source_type != DATA_SOURCE:
            raise ValueError("ReplayTransition.source_type must equal paper_default_terminal_exposure_probe.")
        if self.pending_at_horizon and self.terminal:
            raise ValueError("Pending-at-horizon transitions must remain non-terminal.")
        if self.reward_available:
            if not self.terminal:
                raise ValueError("Only terminal completion/drop transitions may mark reward_available=true.")
            if self.terminal_reason not in {"completed", "dropped"}:
                raise ValueError("Terminal reward-bearing transitions must end in completion or drop.")
        if self.terminal and self.terminal_reason not in {"completed", "dropped", "pending_at_horizon"}:
            raise ValueError("Terminal transitions must have a recognized terminal_reason.")


class ReplayBuffer:
    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("ReplayBuffer.capacity must be positive.")
        self.capacity = capacity
        self._transitions: deque[ReplayTransition] = deque(maxlen=capacity)

    def __len__(self) -> int:
        return len(self._transitions)

    def add(self, transition: ReplayTransition) -> None:
        self._transitions.append(transition)

    def as_list(self) -> list[ReplayTransition]:
        return list(self._transitions)
