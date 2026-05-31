from __future__ import annotations

import math

from collections.abc import Iterable

from .task import Task


def emit_delayed_reward(task: Task) -> None:
    task.reward_emitted = True


def phi_private(psi_priv: int, t: int) -> int:
    return psi_priv - t + 1


def _term_selected(term: object) -> bool:
    if isinstance(term, dict):
        for key in ("selected", "d", "d_selected", "is_selected"):
            if key in term:
                return bool(term[key])
        raise ValueError("public term dictionary must include a selected flag")
    if isinstance(term, tuple) and len(term) >= 2:
        return bool(term[0])
    if isinstance(term, list) and len(term) >= 2:
        return bool(term[0])
    raise ValueError("public term must be a mapping or 2-item sequence")


def _term_psi_pub(term: object) -> int:
    if isinstance(term, dict):
        for key in ("psi_pub", "psi", "value"):
            if key in term:
                return int(term[key])
        raise ValueError("public term dictionary must include a psi_pub value")
    if isinstance(term, tuple) and len(term) >= 2:
        return int(term[1])
    if isinstance(term, list) and len(term) >= 2:
        return int(term[1])
    raise ValueError("public term must be a mapping or 2-item sequence")


def phi_public(selected_terms: Iterable[object], t: int) -> int:
    total = 0
    for term in selected_terms:
        if _term_selected(term):
            total += _term_psi_pub(term) - t + 1
    return total


def select_phi(d1_local: int | bool, phi_priv: int, phi_pub: int) -> int:
    return phi_priv if bool(d1_local) else phi_pub


def validate_terminal_state(terminal_status: str, terminal_slot: int | None, drop_reason: str | None) -> None:
    completed_statuses = {"completed_private", "completed_public", "completed_cloud"}
    dropped_statuses = {"dropped_timeout", "dropped_unavailable"}
    if terminal_status == "pending":
        if terminal_slot is not None or drop_reason is not None:
            raise ValueError("pending terminal state must not carry terminal evidence or drop reason")
        return
    if terminal_status in completed_statuses:
        if terminal_slot is None:
            raise ValueError("completed terminal states require a terminal_slot")
        if drop_reason is not None:
            raise ValueError("completed terminal states must not have a drop_reason")
        return
    if terminal_status in dropped_statuses:
        if terminal_slot is None:
            raise ValueError("dropped terminal states require a terminal_slot")
        if not drop_reason:
            raise ValueError("dropped terminal states require a drop_reason")
        return
    raise ValueError("unsupported terminal_status")


def can_emit_reward(terminal_status: str) -> bool:
    if terminal_status == "pending":
        return False
    if terminal_status in {"completed_private", "completed_public", "completed_cloud", "dropped_timeout", "dropped_unavailable"}:
        return True
    raise ValueError("unsupported terminal_status")


def reward_slot_for_terminal(terminal_slot: int) -> int:
    return terminal_slot + 1


def reward_from_terminal_state(
    x_active: int | bool,
    terminal_status: str,
    phi_value: int | float | None,
    drop_penalty: int | float,
) -> float:
    if not bool(x_active):
        return math.nan
    if terminal_status == "pending":
        raise ValueError("reward cannot be emitted before terminal evidence exists")
    if terminal_status in {"completed_private", "completed_public", "completed_cloud"}:
        if phi_value is None:
            raise ValueError("phi_value is required for completed terminal states")
        return -float(phi_value)
    if terminal_status in {"dropped_timeout", "dropped_unavailable"}:
        return -float(drop_penalty)
    raise ValueError("unsupported terminal_status")


def reward_for_terminal_task(task: Task, *, drop_penalty: float = 40.0) -> float:
    if task.terminal_outcome == "completed" and task.completion_slot is not None:
        return -float(task.completion_slot - task.arrival_slot)
    if task.terminal_outcome == "dropped":
        return -float(drop_penalty)
    raise ValueError("Reward is only defined for completed or dropped tasks")
