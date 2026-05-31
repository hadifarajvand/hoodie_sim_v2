from __future__ import annotations

from dataclasses import dataclass
from typing import Any


_ALLOWED_RUNTIME_MODES = {"paper", "compatibility"}
_ALLOWED_COMPLETION_KINDS = {"private", "public", "cloud"}


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


def compute_absolute_deadline(arrival_slot: int, phi: int) -> int:
    return arrival_slot + phi - 1


def _validate_mode(mode: str) -> None:
    if mode not in _ALLOWED_RUNTIME_MODES:
        raise ValueError(f"mode must be one of {sorted(_ALLOWED_RUNTIME_MODES)}")


def is_success_before_deadline(
    completion_slot: int | None,
    arrival_slot: int,
    phi: int,
    mode: str = "paper",
) -> bool:
    _validate_mode(mode)
    if completion_slot is None:
        return False
    deadline_slot = compute_absolute_deadline(arrival_slot, phi)
    if mode == "paper":
        return completion_slot < deadline_slot
    return completion_slot <= deadline_slot


def terminal_status_from_completion(
    completion_slot: int | None,
    arrival_slot: int,
    phi: int,
    completion_kind: str = "private",
    mode: str = "paper",
) -> str:
    _validate_mode(mode)
    if completion_kind not in _ALLOWED_COMPLETION_KINDS:
        raise ValueError(f"completion_kind must be one of {sorted(_ALLOWED_COMPLETION_KINDS)}")
    if is_success_before_deadline(completion_slot, arrival_slot, phi, mode=mode):
        return {
            "private": "completed_private",
            "public": "completed_public",
            "cloud": "completed_cloud",
        }[completion_kind]
    return "dropped_timeout"


def build_timeout_contract(
    *,
    arrival_slot: int,
    timeout_phi: int,
    completion_slot: int | None,
    mode: str = "paper",
) -> PaperTimeoutContract:
    deadline_slot = compute_absolute_deadline(arrival_slot, timeout_phi)
    dropped = not is_success_before_deadline(completion_slot, arrival_slot, timeout_phi, mode=mode)
    return PaperTimeoutContract(
        arrival_slot=arrival_slot,
        timeout_phi=timeout_phi,
        deadline_slot=deadline_slot,
        completion_slot=completion_slot,
        dropped_due_to_timeout=dropped,
    )
