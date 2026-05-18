from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import torch

from .config import SMOKE_ACTION_COUNT, SMOKE_DATA_SOURCE, SMOKE_LOOKBACK_W, SmokeTrainingConfig


@dataclass(slots=True, frozen=True)
class SmokeReplayTransition:
    transition_id: str
    state_window: tuple[tuple[float, float, float], ...]
    next_state_window: tuple[tuple[float, float, float], ...]
    action_index: int
    legal_action_mask: tuple[bool, bool, bool]
    reward_available: bool
    reward_value: float
    is_terminal: bool
    pending_at_horizon: bool
    data_source: str = SMOKE_DATA_SOURCE
    smoke_target_value: float = 0.0

    def __post_init__(self) -> None:
        if len(self.state_window) != SMOKE_LOOKBACK_W:
            raise ValueError("SmokeReplayTransition.state_window must use lookback_w=10.")
        if len(self.next_state_window) != SMOKE_LOOKBACK_W:
            raise ValueError("SmokeReplayTransition.next_state_window must use lookback_w=10.")
        if self.action_index not in {0, 1, 2}:
            raise ValueError("SmokeReplayTransition.action_index must be one of {0,1,2}.")
        if len(self.legal_action_mask) != SMOKE_ACTION_COUNT:
            raise ValueError("SmokeReplayTransition.legal_action_mask must have three entries.")
        if self.reward_available and not self.is_terminal:
            raise ValueError("Only terminal transitions may mark reward_available=true.")
        if self.pending_at_horizon and self.is_terminal:
            raise ValueError("Pending-at-horizon transitions must remain non-terminal.")
        if self.data_source != SMOKE_DATA_SOURCE:
            raise ValueError("SmokeReplayTransition.data_source must be smoke_fixture.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "transition_id": self.transition_id,
            "state_window": [list(row) for row in self.state_window],
            "next_state_window": [list(row) for row in self.next_state_window],
            "action_index": self.action_index,
            "legal_action_mask": list(self.legal_action_mask),
            "reward_available": self.reward_available,
            "reward_value": self.reward_value,
            "is_terminal": self.is_terminal,
            "pending_at_horizon": self.pending_at_horizon,
            "data_source": self.data_source,
            "smoke_target_value": self.smoke_target_value,
        }


@dataclass(slots=True)
class SmokeBatchSummary:
    batch_size: int
    terminal_count: int
    non_terminal_count: int
    pending_count: int
    reward_bearing_count: int
    seed_signature: str
    data_source: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "batch_size": self.batch_size,
            "terminal_count": self.terminal_count,
            "non_terminal_count": self.non_terminal_count,
            "pending_count": self.pending_count,
            "reward_bearing_count": self.reward_bearing_count,
            "seed_signature": self.seed_signature,
            "data_source": self.data_source,
        }


@dataclass(slots=True)
class SmokeBatch:
    transitions: tuple[SmokeReplayTransition, ...]
    state_tensor: torch.Tensor
    next_state_tensor: torch.Tensor
    action_index_tensor: torch.Tensor
    legal_action_mask_tensor: torch.Tensor
    reward_available_tensor: torch.Tensor
    reward_value_tensor: torch.Tensor
    terminal_tensor: torch.Tensor
    pending_at_horizon_tensor: torch.Tensor
    smoke_target_tensor: torch.Tensor
    summary: SmokeBatchSummary

    def to_dict(self) -> dict[str, Any]:
        return {
            "transitions": [transition.to_dict() for transition in self.transitions],
            "summary": self.summary.to_dict(),
        }


def _fixture_window(base: float) -> tuple[tuple[float, float, float], ...]:
    rows: list[tuple[float, float, float]] = []
    for slot in range(SMOKE_LOOKBACK_W):
        rows.append(
            (
                round(base + slot * 0.1, 4),
                round(base * 0.5 + slot * 0.05, 4),
                round(((slot % 3) - 1) * 0.25 + base * 0.1, 4),
            )
        )
    return tuple(rows)


def _build_transitions() -> tuple[SmokeReplayTransition, ...]:
    return (
        SmokeReplayTransition(
            transition_id="smoke-fixture-0",
            state_window=_fixture_window(1.0),
            next_state_window=_fixture_window(1.5),
            action_index=1,
            legal_action_mask=(True, True, True),
            reward_available=False,
            reward_value=0.0,
            is_terminal=False,
            pending_at_horizon=True,
            smoke_target_value=-10.0,
        ),
        SmokeReplayTransition(
            transition_id="smoke-fixture-1",
            state_window=_fixture_window(-1.0),
            next_state_window=_fixture_window(-0.5),
            action_index=2,
            legal_action_mask=(True, True, True),
            reward_available=True,
            reward_value=1.0,
            is_terminal=True,
            pending_at_horizon=False,
            smoke_target_value=10.0,
        ),
    )


def build_smoke_batch(config: SmokeTrainingConfig) -> SmokeBatch:
    transitions = _build_transitions()
    state_tensor = torch.tensor([transition.state_window for transition in transitions], dtype=torch.float32)
    next_state_tensor = torch.tensor([transition.next_state_window for transition in transitions], dtype=torch.float32)
    action_index_tensor = torch.tensor([transition.action_index for transition in transitions], dtype=torch.long)
    legal_action_mask_tensor = torch.tensor([transition.legal_action_mask for transition in transitions], dtype=torch.bool)
    reward_available_tensor = torch.tensor([transition.reward_available for transition in transitions], dtype=torch.bool)
    reward_value_tensor = torch.tensor([transition.reward_value for transition in transitions], dtype=torch.float32)
    terminal_tensor = torch.tensor([transition.is_terminal for transition in transitions], dtype=torch.bool)
    pending_at_horizon_tensor = torch.tensor([transition.pending_at_horizon for transition in transitions], dtype=torch.bool)
    smoke_target_tensor = torch.tensor([transition.smoke_target_value for transition in transitions], dtype=torch.float32)

    summary = SmokeBatchSummary(
        batch_size=len(transitions),
        terminal_count=int(terminal_tensor.sum().item()),
        non_terminal_count=int((~terminal_tensor).sum().item()),
        pending_count=int(pending_at_horizon_tensor.sum().item()),
        reward_bearing_count=int(reward_available_tensor.sum().item()),
        seed_signature=config.seed_bundle.signature if config.seed_bundle else "unset",
        data_source=SMOKE_DATA_SOURCE,
    )

    return SmokeBatch(
        transitions=transitions,
        state_tensor=state_tensor,
        next_state_tensor=next_state_tensor,
        action_index_tensor=action_index_tensor,
        legal_action_mask_tensor=legal_action_mask_tensor,
        reward_available_tensor=reward_available_tensor,
        reward_value_tensor=reward_value_tensor,
        terminal_tensor=terminal_tensor,
        pending_at_horizon_tensor=pending_at_horizon_tensor,
        smoke_target_tensor=smoke_target_tensor,
        summary=summary,
    )
