from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@dataclass(slots=True)
class PolicyContext:
    observation: dict[str, object]
    legal_action_mask: dict[str, bool]
    trace_history: tuple[object, ...] = field(default_factory=tuple)
    dal_advisory: dict[str, object] | None = None


@runtime_checkable
class SharedPolicy(Protocol):
    def choose_action(self, context: PolicyContext) -> str:
        """Return one action for the current task."""
