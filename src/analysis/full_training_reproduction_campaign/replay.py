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

SEMANTICS_TO_ACTION_INDEX: dict[str, int] = {value: key for key, value in ACTION_INDEX_TO_SEMANTICS.items()}

PAPER_STATE_DIM = 74
PAPER_ACTION_COUNT = 22
PAPER_LOOKBACK_W = 10

ACTION_INDEX_TO_SEMANTICS_PAPER: dict[int, str] = {
    0: "local",
    21: "cloud",
}
for _i in range(1, PAPER_ACTION_COUNT - 1):
    ACTION_INDEX_TO_SEMANTICS_PAPER[_i] = f"horizontal_{_i}"

SEMANTICS_TO_ACTION_INDEX_PAPER: dict[str, int] = {value: key for key, value in ACTION_INDEX_TO_SEMANTICS_PAPER.items()}

STATE_DIM = 3
LOOKBACK_W = 10
DATA_SOURCE = "environment_rollout"


def zero_state_row(state_dim: int = STATE_DIM) -> tuple[float, ...]:
    return tuple(0.0 for _ in range(state_dim))


def build_state_window(history: Iterable[tuple[float, ...]], *, lookback_w: int = LOOKBACK_W, state_dim: int = STATE_DIM) -> tuple[tuple[float, ...], ...]:
    rows = list(history)[-lookback_w:]
    if len(rows) < lookback_w:
        dim = len(rows[0]) if rows else state_dim
        padding = [zero_state_row(dim) for _ in range(lookback_w - len(rows))]
        rows = padding + rows
    return tuple(rows)


def build_state_window_tensor(window: tuple[tuple[float, ...], ...], *, device: torch.device | None = None) -> torch.Tensor:
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


def legal_action_mask_to_tuple(mask: dict[str, bool], *, action_count: int = 3) -> tuple[bool, ...]:
    if action_count == 3:
        return (bool(mask.get("local", False)), bool(mask.get("horizontal", False)), bool(mask.get("vertical", False)))
    local_legal = bool(mask.get("local", False)) or bool(mask.get("compute_local", False))
    horizontal_legal = bool(mask.get("horizontal", False)) or bool(mask.get("offload_horizontal", False))
    cloud_legal = bool(mask.get("vertical", False)) or bool(mask.get("offload_vertical", False)) or bool(mask.get("cloud", False))
    result = [False] * action_count
    result[0] = local_legal
    if horizontal_legal:
        for i in range(1, action_count - 1):
            result[i] = True
    if cloud_legal:
        result[action_count - 1] = True
    return tuple(result)


def action_index_to_semantics(action_index: int) -> str:
    try:
        return ACTION_INDEX_TO_SEMANTICS[action_index]
    except KeyError as exc:  # pragma: no cover - defensive
        raise ValueError(f"Unsupported action index: {action_index}") from exc


def semantics_to_action_index(semantics: str) -> int:
    if semantics in SEMANTICS_TO_ACTION_INDEX_PAPER:
        return SEMANTICS_TO_ACTION_INDEX_PAPER[semantics]
    try:
        return SEMANTICS_TO_ACTION_INDEX[semantics]
    except KeyError as exc:  # pragma: no cover - defensive
        raise ValueError(f"Unsupported action semantics: {semantics}") from exc


@dataclass(slots=True, frozen=True)
class ReplayTransition:
    state: tuple[tuple[float, ...], ...]
    action: int
    legal_action_mask: tuple[bool, ...]
    next_state: tuple[tuple[float, ...], ...]
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
    state_dim: int = STATE_DIM
    action_count: int = 3
    source_type: str = DATA_SOURCE

    def __post_init__(self) -> None:
        if len(self.state) != LOOKBACK_W:
            raise ValueError("ReplayTransition.state must contain ten history rows.")
        if len(self.next_state) != LOOKBACK_W:
            raise ValueError("ReplayTransition.next_state must contain ten history rows.")
        if self.state and any(len(row) != self.state_dim for row in self.state):
            raise ValueError(f"ReplayTransition.state rows must have {self.state_dim} elements, got row lengths { {len(row) for row in self.state} }.")
        if self.next_state and any(len(row) != self.state_dim for row in self.next_state):
            raise ValueError(f"ReplayTransition.next_state rows must have {self.state_dim} elements.")
        if not (0 <= self.action < self.action_count):
            raise ValueError(f"ReplayTransition.action must be between 0 and {self.action_count - 1}, got {self.action}.")
        if len(self.legal_action_mask) != self.action_count:
            raise ValueError(f"ReplayTransition.legal_action_mask must contain {self.action_count} entries, got {len(self.legal_action_mask)}.")
        if self.source_type != DATA_SOURCE:
            raise ValueError("ReplayTransition.source_type must equal environment_rollout.")
        if self.pending_at_horizon and self.terminal:
            raise ValueError("Pending-at-horizon transitions must remain non-terminal.")
        if self.reward_available:
            if not self.terminal:
                raise ValueError("Only terminal completion/drop transitions may mark reward_available=true.")
            if self.terminal_reason not in {"completed", "dropped"}:
                raise ValueError("Terminal reward-bearing transitions must end in completion or drop.")
        if self.terminal and self.terminal_reason not in {"completed", "dropped", "pending_at_horizon"}:
            raise ValueError("Terminal transitions must have a recognized terminal_reason.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": [list(row) for row in self.state],
            "action": self.action,
            "legal_action_mask": list(self.legal_action_mask),
            "next_state": [list(row) for row in self.next_state],
            "reward": self.reward,
            "reward_available": self.reward_available,
            "terminal": self.terminal,
            "terminal_reason": self.terminal_reason,
            "pending_at_horizon": self.pending_at_horizon,
            "arrival_slot": self.arrival_slot,
            "completion_or_drop_slot": self.completion_or_drop_slot,
            "agent_id": self.agent_id,
            "episode_id": self.episode_id,
            "step_id": self.step_id,
            "source_type": self.source_type,
        }


@dataclass(slots=True)
class ReplayBatch:
    transitions: tuple[ReplayTransition, ...]
    state_tensor: torch.Tensor
    next_state_tensor: torch.Tensor
    action_tensor: torch.Tensor
    legal_action_mask_tensor: torch.Tensor
    reward_tensor: torch.Tensor
    reward_available_tensor: torch.Tensor
    terminal_tensor: torch.Tensor
    pending_at_horizon_tensor: torch.Tensor

    def to_dict(self) -> dict[str, Any]:
        return {
            "transitions": [transition.to_dict() for transition in self.transitions],
            "batch_size": len(self.transitions),
        }


class ReplayBuffer:
    def __init__(self, capacity: int, *, seed: int) -> None:
        if capacity <= 0:
            raise ValueError("ReplayBuffer.capacity must be positive.")
        self.capacity = capacity
        self._transitions: deque[ReplayTransition] = deque(maxlen=capacity)
        self._seed = seed

    def __len__(self) -> int:
        return len(self._transitions)

    def add(self, transition: ReplayTransition) -> None:
        self._transitions.append(transition)

    def as_list(self) -> list[ReplayTransition]:
        return list(self._transitions)

    def sample(self, batch_size: int, *, rng) -> ReplayBatch:
        if len(self._transitions) < batch_size:
            raise ValueError("ReplayBuffer does not contain enough transitions for the requested batch size.")
        indices = sorted(rng.sample(range(len(self._transitions)), batch_size))
        transitions = tuple(self._transitions[index] for index in indices)
        return self._to_batch(transitions)

    def _to_batch(self, transitions: tuple[ReplayTransition, ...]) -> ReplayBatch:
        state_tensor = torch.tensor([transition.state for transition in transitions], dtype=torch.float32)
        next_state_tensor = torch.tensor([transition.next_state for transition in transitions], dtype=torch.float32)
        action_tensor = torch.tensor([transition.action for transition in transitions], dtype=torch.long)
        legal_action_mask_tensor = torch.tensor([transition.legal_action_mask for transition in transitions], dtype=torch.bool)
        reward_tensor = torch.tensor([transition.reward for transition in transitions], dtype=torch.float32)
        reward_available_tensor = torch.tensor([transition.reward_available for transition in transitions], dtype=torch.bool)
        terminal_tensor = torch.tensor([transition.terminal for transition in transitions], dtype=torch.bool)
        pending_at_horizon_tensor = torch.tensor([transition.pending_at_horizon for transition in transitions], dtype=torch.bool)
        return ReplayBatch(
            transitions=transitions,
            state_tensor=state_tensor,
            next_state_tensor=next_state_tensor,
            action_tensor=action_tensor,
            legal_action_mask_tensor=legal_action_mask_tensor,
            reward_tensor=reward_tensor,
            reward_available_tensor=reward_available_tensor,
            terminal_tensor=terminal_tensor,
            pending_at_horizon_tensor=pending_at_horizon_tensor,
        )
