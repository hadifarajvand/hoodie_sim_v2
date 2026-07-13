from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@dataclass(slots=True)
class PolicyContext:
    observation: dict[str, object]
    legal_action_mask: dict[str, bool]
    trace_history: tuple[object, ...] = field(default_factory=tuple)


@runtime_checkable
class SharedPolicy(Protocol):
    def choose_action(self, context: PolicyContext) -> str:
        """Return one action for the current task."""


@runtime_checkable
class ReplayTrainablePolicy(SharedPolicy, Protocol):
    def record_transition(
        self,
        state: dict[str, object],
        action: str,
        reward: float,
        next_state: dict[str, object],
        done: bool,
        *,
        delta_slots: int = 1,
    ) -> None:
        """Persist one replay transition."""

    def learn_from_replay(self, batch_size: int, learning_rate: float) -> int:
        """Run one replay-backed learner step when enough data exists."""

    def sync_target_network(self) -> None:
        """Synchronize online and target parameters when policy uses them."""

