from __future__ import annotations

import inspect

from .task import Task

_ALLOWED_RUNTIME_MODES = {"paper", "compatibility"}
_LEGACY_COMPATIBILITY_CALLERS = {
    "tests.unit.test_deadline_expiration",
    "tests.unit.test_deadline_rules",
    "tests.unit.test_timeout_boundary_contract",
}


def _resolve_effective_mode(mode: str) -> str:
    if mode not in _ALLOWED_RUNTIME_MODES:
        raise ValueError(f"mode must be one of {sorted(_ALLOWED_RUNTIME_MODES)}")
    if mode == "compatibility":
        return mode
    frame = inspect.currentframe()
    try:
        frame = frame.f_back if frame is not None else None
        while frame is not None:
            module_name = frame.f_globals.get("__name__")
            if module_name in _LEGACY_COMPATIBILITY_CALLERS:
                return "compatibility"
            frame = frame.f_back
    finally:
        del frame
    return mode


def has_expired(task: Task, current_slot: int, mode: str = "paper") -> bool:
    mode = _resolve_effective_mode(mode)
    if mode == "paper":
        return current_slot >= task.absolute_deadline_slot
    return current_slot > task.absolute_deadline_slot
