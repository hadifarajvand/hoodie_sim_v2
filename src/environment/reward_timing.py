from __future__ import annotations

from .task import Task


def emit_delayed_reward(task: Task) -> None:
    task.reward_emitted = True


def reward_for_terminal_task(task: Task, *, drop_penalty: float = 40.0) -> float:
    if task.terminal_outcome == "completed" and task.completion_slot is not None:
        return -float(task.completion_slot - task.arrival_slot)
    if task.terminal_outcome == "dropped":
        return -float(drop_penalty)
    raise ValueError("Reward is only defined for completed or dropped tasks")
