from __future__ import annotations

from .deadline_rules import has_expired
from .reward_timing import emit_delayed_reward
from .task import Task


def resolve_terminal_state(task: Task, current_slot: int) -> str | None:
    if task.completion_slot is not None and task.completion_slot <= task.absolute_deadline_slot:
        task.terminal_outcome = "completed"
        return "completed"
    if has_expired(task, current_slot):
        task.terminal_outcome = "dropped"
        task.drop_flag = True
        return "dropped"
    return None


def emit_reward_if_terminal(task: Task) -> None:
    if task.terminal_outcome in {"completed", "dropped"} and not task.reward_emitted:
        emit_delayed_reward(task)

