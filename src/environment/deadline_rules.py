from __future__ import annotations

from .task import Task
from .paper_timeout import compute_absolute_deadline, is_success_before_deadline, terminal_status_from_completion


def has_expired(task: Task, current_slot: int) -> bool:
    return current_slot > task.absolute_deadline_slot
