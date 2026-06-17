from __future__ import annotations

from .task import Task

_ALLOWED_RUNTIME_MODES = {"paper", "compatibility"}


def _validate_mode(mode: str) -> None:
    if mode not in _ALLOWED_RUNTIME_MODES:
        raise ValueError(f"mode must be one of {sorted(_ALLOWED_RUNTIME_MODES)}")


def has_expired(task: Task, current_slot: int, mode: str = "paper") -> bool:
    _validate_mode(mode)
    if mode == "paper":
        return current_slot > task.absolute_deadline_slot
    return current_slot > task.absolute_deadline_slot
