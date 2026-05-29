from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class PaperTimeoutContract:
    arrival_slot: int
    timeout_phi: int
    deadline_slot: int
    completion_slot: int | None
    dropped_due_to_timeout: bool
    timeout_semantics_version: str = "timeout_arrival_plus_phi_minus_one_v1"

    def to_dict(self) -> dict[str, Any]:
        return {
            "arrival_slot": self.arrival_slot,
            "timeout_phi": self.timeout_phi,
            "deadline_slot": self.deadline_slot,
            "completion_slot": self.completion_slot,
            "dropped_due_to_timeout": self.dropped_due_to_timeout,
            "timeout_semantics_version": self.timeout_semantics_version,
        }


def build_timeout_contract(*, arrival_slot: int, timeout_phi: int, completion_slot: int | None) -> PaperTimeoutContract:
    deadline_slot = arrival_slot + timeout_phi - 1
    dropped = completion_slot is None or completion_slot > deadline_slot
    return PaperTimeoutContract(arrival_slot=arrival_slot, timeout_phi=timeout_phi, deadline_slot=deadline_slot, completion_slot=completion_slot, dropped_due_to_timeout=dropped)

