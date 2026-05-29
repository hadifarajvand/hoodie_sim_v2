from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class RecoverySnapshot:
    recovery_used: bool
    recovery_reason: str
    recovery_source: str
    previous_load_snapshot_used: bool
    previous_forecast_input_used: bool
    recovered_load_snapshot: dict[str, Any] | None
    recovery_version: str = "paper_recovery_v1"

    def to_dict(self) -> dict[str, Any]:
        return {
            "recovery_used": self.recovery_used,
            "recovery_reason": self.recovery_reason,
            "recovery_source": self.recovery_source,
            "previous_load_snapshot_used": self.previous_load_snapshot_used,
            "previous_forecast_input_used": self.previous_forecast_input_used,
            "recovered_load_snapshot": self.recovered_load_snapshot,
            "recovery_version": self.recovery_version,
        }


def recover_load_snapshot(*, current_snapshot: dict[str, Any] | None, previous_snapshot: dict[str, Any] | None, previous_forecast_input: dict[str, Any] | None) -> RecoverySnapshot:
    if current_snapshot is not None:
        return RecoverySnapshot(False, "current_snapshot_available", "current", False, False, current_snapshot)
    if previous_snapshot is not None:
        return RecoverySnapshot(True, "reused_previous_valid_snapshot", "previous_load_snapshot", True, False, previous_snapshot)
    return RecoverySnapshot(True, "reused_previous_forecast_input", "previous_forecast_input", False, True, previous_forecast_input)

