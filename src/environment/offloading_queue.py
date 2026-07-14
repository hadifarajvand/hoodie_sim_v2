from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Deque

from .task import Task


@dataclass(slots=True)
class OffloadingQueue:
    owner_node_id: str
    resolved_destination: str | None = None
    tasks: Deque[Task] = field(default_factory=deque)
    current_head_entered_at: int | None = None

    def enqueue(self, task: Task, slot: int) -> None:
        if not self.tasks:
            self.current_head_entered_at = slot
        self.tasks.append(task)
        task.metadata["queue_entered_at"] = slot
        task.queue_state = "offloading_queue"
        # Queue admission is not transmission start.  Only the head receives a
        # start timestamp when the physical transmitter becomes available.
        task.transmission_start_slot = None
        task.metadata.pop("transmission_start_slot", None)
        task.metadata.pop("transmission_started_at", None)

    def dequeue(self) -> Task:
        task = self.tasks.popleft()
        if self.tasks:
            next_head = self.tasks[0]
            self.current_head_entered_at = int(next_head.metadata.get("queue_entered_at", 0))
            next_head.transmission_start_slot = None
            next_head.metadata.pop("transmission_start_slot", None)
            next_head.metadata.pop("transmission_started_at", None)
        else:
            self.current_head_entered_at = None
        return task

    def waiting_time(self, current_slot: int) -> int:
        if self.current_head_entered_at is None:
            return 0
        return max(0, current_slot - self.current_head_entered_at)
