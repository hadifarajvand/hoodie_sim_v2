from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EdgeAgentState:
    agent_id: int
    queue_reference: Any | None = None
    cpu_slots: int = 0
    active_tasks: list[int] = field(default_factory=list)
    last_decision_snapshot: dict[str, Any] = field(default_factory=dict)
