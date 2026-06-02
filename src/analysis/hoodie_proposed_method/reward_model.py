from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .formulas import compute_private_cost, compute_public_cost, compute_reward


@dataclass(frozen=True, slots=True)
class RewardCostOutcome:
    task_present: bool
    terminal_status: str
    phi_value: int | float | None
    drop_cost: float
    reward_value: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def private_cost(psi_priv: int, t: int) -> int:
    return compute_private_cost(psi_priv=psi_priv, t=t)


def public_cost(destination_completion_slot: int, arrival_slot: int) -> int:
    return compute_public_cost(destination_completion_slot=destination_completion_slot, arrival_slot=arrival_slot)


def reward_from_task_outcome(
    *,
    task_present: bool,
    terminal_status: str,
    phi_value: int | float | None,
    drop_cost: float = 40.0,
) -> RewardCostOutcome:
    reward_value = compute_reward(
        task_present=task_present,
        terminal_status=terminal_status,
        phi_value=phi_value,
        drop_cost=drop_cost,
    )
    return RewardCostOutcome(
        task_present=task_present,
        terminal_status=terminal_status,
        phi_value=phi_value,
        drop_cost=float(drop_cost),
        reward_value=reward_value,
    )
