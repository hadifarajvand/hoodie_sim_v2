from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(slots=True)
class Task:
    task_id: int
    source_agent_id: int
    arrival_slot: int
    size: float
    processing_density: float
    timeout_length: int
    absolute_deadline_slot: int
    cycles_required: float = 0.0
    cycles_remaining: float = 0.0
    selected_action: Optional[str] = None
    resolved_destination: Optional[str] = None
    queue_state: str = "created"
    start_slot: Optional[int] = None
    completion_slot: Optional[int] = None
    terminal_outcome: Optional[str] = None
    reward_emitted: bool = False
    drop_flag: bool = False
    metadata: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.size = float(self.size)
        self.processing_density = float(self.processing_density)
        self.cycles_required = float(self.cycles_required or self.size * self.processing_density)
        self.cycles_remaining = float(self.cycles_remaining or self.cycles_required)
        if self.cycles_remaining > self.cycles_required:
            self.cycles_remaining = float(self.cycles_required)
