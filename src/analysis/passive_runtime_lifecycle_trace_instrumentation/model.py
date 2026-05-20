from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class BehaviorEquivalenceCheck:
    name: str
    verified: bool
    details: str

    def to_dict(self) -> dict[str, object]:
        return {"name": self.name, "verified": self.verified, "details": self.details}


@dataclass(frozen=True, slots=True)
class LifecycleTraceSummary:
    strategy: str
    seed: int
    trace_enabled: bool
    event_types_seen: tuple[str, ...]
    event_counts: dict[str, int]
    execution_progress_count: int
    completed_count: int
    dropped_count: int
    pending_at_horizon_count: int
    reward_emitted_count: int
    per_task_event_order: dict[str, list[str]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "strategy": self.strategy,
            "seed": self.seed,
            "trace_enabled": self.trace_enabled,
            "event_types_seen": list(self.event_types_seen),
            "event_counts": dict(self.event_counts),
            "execution_progress_count": self.execution_progress_count,
            "completed_count": self.completed_count,
            "dropped_count": self.dropped_count,
            "pending_at_horizon_count": self.pending_at_horizon_count,
            "reward_emitted_count": self.reward_emitted_count,
            "per_task_event_order": {key: list(value) for key, value in self.per_task_event_order.items()},
        }

