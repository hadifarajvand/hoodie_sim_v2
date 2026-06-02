from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class PubSubRecoveryMetadata:
    source_agent_id: str
    destination_agent_id: str
    broker_id: str
    slot: int
    delayed: bool
    stale: bool
    recovery_window: int

    def __post_init__(self) -> None:
        if not self.source_agent_id:
            raise ValueError("source_agent_id must be non-empty")
        if not self.destination_agent_id:
            raise ValueError("destination_agent_id must be non-empty")
        if not self.broker_id:
            raise ValueError("broker_id must be non-empty")
        if self.recovery_window <= 0:
            raise ValueError("recovery_window must be positive")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class EdgeControllerBroker:
    broker_id: str
    managed_agent_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.broker_id:
            raise ValueError("broker_id must be non-empty")
        if not self.managed_agent_ids:
            raise ValueError("managed_agent_ids must be non-empty")

    def route(self, source_agent_id: str, destination_agent_id: str, slot: int, delayed: bool = False, stale: bool = False, recovery_window: int = 1) -> PubSubRecoveryMetadata:
        if source_agent_id not in self.managed_agent_ids:
            raise ValueError("source_agent_id must be managed by this broker")
        if destination_agent_id not in self.managed_agent_ids and destination_agent_id != "cloud":
            raise ValueError("destination_agent_id must be managed by this broker or cloud")
        return PubSubRecoveryMetadata(
            source_agent_id=source_agent_id,
            destination_agent_id=destination_agent_id,
            broker_id=self.broker_id,
            slot=slot,
            delayed=delayed,
            stale=stale,
            recovery_window=recovery_window,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
