from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Deque

from .task import Task


@dataclass(slots=True)
class PrivateQueue:
    owner_node_id: str
    tasks: Deque[Task] = field(default_factory=deque)
    current_head_entered_at: int | None = None

    def enqueue(self, task: Task, slot: int) -> None:
        if not self.tasks:
            self.current_head_entered_at = slot
        self.tasks.append(task)
        task.metadata["queue_entered_at"] = slot
        task.queue_state = "private_queue"
        task.computation_start_slot = task.computation_start_slot if task.computation_start_slot is not None else int(slot)
        task.metadata["computation_start_slot"] = task.computation_start_slot

    def dequeue(self) -> Task:
        task = self.tasks.popleft()
        if self.tasks:
            next_head = self.tasks[0]
            self.current_head_entered_at = int(next_head.metadata.get("queue_entered_at", 0))
        else:
            self.current_head_entered_at = None
        return task

    def waiting_time(self, current_slot: int) -> int:
        if self.current_head_entered_at is None:
            return 0
        return max(0, current_slot - self.current_head_entered_at)
