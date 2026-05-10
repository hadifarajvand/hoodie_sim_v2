from __future__ import annotations

from .task import Task


def has_expired(task: Task, current_slot: int) -> bool:
    return current_slot >= task.absolute_deadline_slot
