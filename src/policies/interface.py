from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    action: str
    policy_name: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PolicyContext:
    observation: dict[str, object]
    legal_action_mask: dict[str, bool]
    trace_history: tuple[object, ...] = field(default_factory=tuple)


@runtime_checkable
class SharedPolicy(Protocol):
    policy_name: str

    def choose_action(self, context: PolicyContext) -> str:
        ...

    def choose(self, context: PolicyContext) -> PolicyDecision:
        return PolicyDecision(action=self.choose_action(context), policy_name=self.policy_name)


@runtime_checkable
class ReplayTrainablePolicy(SharedPolicy, Protocol):
    def record_transition(self, state, action, reward, next_state, done, *, delta_slots: int = 1) -> None:
        ...

    def learn_from_replay(self, batch_size: int, learning_rate: float) -> int:
        ...

    def sync_target_network(self) -> None:
        ...
