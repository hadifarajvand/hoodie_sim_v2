from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


def _clamp_completion(completion_slot: int, timeout_slot: int) -> int:
    return min(completion_slot, timeout_slot)


@dataclass(frozen=True, slots=True)
class PrivateQueueTiming:
    arrival_slot: int
    previous_max_completion_slot: int
    processing_completion_slot: int
    timeout_slot: int

    @property
    def waiting_start_slot(self) -> int:
        return max(self.arrival_slot, self.previous_max_completion_slot + 1)

    @property
    def waiting_time(self) -> int:
        return self.waiting_start_slot - self.arrival_slot

    @property
    def completion_slot(self) -> int:
        return _clamp_completion(max(self.processing_completion_slot, self.waiting_start_slot), self.timeout_slot)

    @property
    def timed_out(self) -> bool:
        return self.processing_completion_slot > self.timeout_slot

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.update(
            waiting_start_slot=self.waiting_start_slot,
            waiting_time=self.waiting_time,
            completion_slot=self.completion_slot,
            timed_out=self.timed_out,
        )
        return payload


@dataclass(frozen=True, slots=True)
class OffloadingQueueTiming:
    arrival_slot: int
    transmission_completion_slot: int
    timeout_slot: int
    link_rate_kind: str

    def __post_init__(self) -> None:
        if self.link_rate_kind not in {"horizontal", "vertical"}:
            raise ValueError("link_rate_kind must be horizontal or vertical")

    @property
    def completion_slot(self) -> int:
        return _clamp_completion(self.transmission_completion_slot, self.timeout_slot)

    @property
    def timed_out(self) -> bool:
        return self.transmission_completion_slot > self.timeout_slot

    @property
    def transfer_delay(self) -> int:
        return self.completion_slot - self.arrival_slot

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.update(
            completion_slot=self.completion_slot,
            timed_out=self.timed_out,
            transfer_delay=self.transfer_delay,
        )
        return payload


@dataclass(frozen=True, slots=True)
class PublicQueueTiming:
    arrival_slot: int
    destination_completion_slot: int
    timeout_slot: int
    destination_kind: str

    def __post_init__(self) -> None:
        if self.destination_kind not in {"edge_public", "cloud_public"}:
            raise ValueError("destination_kind must be edge_public or cloud_public")

    @property
    def completion_slot(self) -> int:
        return _clamp_completion(self.destination_completion_slot, self.timeout_slot)

    @property
    def timed_out(self) -> bool:
        return self.destination_completion_slot > self.timeout_slot

    @property
    def destination_delay(self) -> int:
        return self.completion_slot - self.arrival_slot

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.update(
            completion_slot=self.completion_slot,
            timed_out=self.timed_out,
            destination_delay=self.destination_delay,
        )
        return payload
