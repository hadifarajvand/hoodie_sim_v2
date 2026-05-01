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
    selected_action: Optional[str] = None
    resolved_destination: Optional[str] = None
    queue_state: str = "created"
    start_slot: Optional[int] = None
    completion_slot: Optional[int] = None
    terminal_outcome: Optional[str] = None
    reward_emitted: bool = False
    drop_flag: bool = False
    metadata: dict[str, object] = field(default_factory=dict)
