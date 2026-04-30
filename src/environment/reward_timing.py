from __future__ import annotations

from .task import Task


def emit_delayed_reward(task: Task) -> None:
    task.reward_emitted = True

