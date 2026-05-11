from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SlotDurationAudit:
    paper_delta_seconds: float
    runtime_delta_seconds: float
    feature_027_reported_slot_duration_seconds: float
    mismatch_status: str
    required_action: str

    def to_dict(self) -> dict[str, object]:
        return {
            "paper_delta_seconds": self.paper_delta_seconds,
            "runtime_delta_seconds": self.runtime_delta_seconds,
            "feature_027_reported_slot_duration_seconds": self.feature_027_reported_slot_duration_seconds,
            "mismatch_status": self.mismatch_status,
            "required_action": self.required_action,
        }


def audit_slot_duration_contract(paper_delta_seconds: float, runtime_delta_seconds: float, feature_027_reported_slot_duration_seconds: float) -> SlotDurationAudit:
    if paper_delta_seconds <= 0:
        raise ValueError("paper_delta_seconds must be greater than zero")
    if runtime_delta_seconds <= 0:
        raise ValueError("runtime_delta_seconds must be greater than zero")
    if feature_027_reported_slot_duration_seconds <= 0:
        raise ValueError("feature_027_reported_slot_duration_seconds must be greater than zero")

    if paper_delta_seconds == runtime_delta_seconds == feature_027_reported_slot_duration_seconds:
        return SlotDurationAudit(
            paper_delta_seconds=paper_delta_seconds,
            runtime_delta_seconds=runtime_delta_seconds,
            feature_027_reported_slot_duration_seconds=feature_027_reported_slot_duration_seconds,
            mismatch_status="matched",
            required_action="none",
        )

    if paper_delta_seconds == runtime_delta_seconds and feature_027_reported_slot_duration_seconds != runtime_delta_seconds:
        return SlotDurationAudit(
            paper_delta_seconds=paper_delta_seconds,
            runtime_delta_seconds=runtime_delta_seconds,
            feature_027_reported_slot_duration_seconds=feature_027_reported_slot_duration_seconds,
            mismatch_status="repaired",
            required_action="regenerate_feature_027_report",
        )

    return SlotDurationAudit(
        paper_delta_seconds=paper_delta_seconds,
        runtime_delta_seconds=runtime_delta_seconds,
        feature_027_reported_slot_duration_seconds=feature_027_reported_slot_duration_seconds,
        mismatch_status="mismatched",
        required_action="repair_runtime_or_regenerate_feature_027_report",
    )
