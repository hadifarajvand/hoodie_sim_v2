from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .settings import SensitivitySetting


def build_baseline_signature(metrics: dict[str, Any]) -> str:
    return (
        f"completed={int(metrics.get('completed_tasks', 0))}"
        f"::dropped={int(metrics.get('dropped_tasks', 0))}"
        f"::throughput={int(metrics.get('throughput', 0))}"
        f"::delay={metrics.get('average_delay', 0)}"
    )


@dataclass(slots=True)
class SettingSignature:
    seed: int
    scenario_name: str
    episode_length: int
    baseline_signatures: dict[str, str]
    distinct_signatures: int
    reference_match: bool
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "seed": self.seed,
            "scenario_name": self.scenario_name,
            "episode_length": self.episode_length,
            "baseline_signatures": dict(self.baseline_signatures),
            "distinct_signatures": self.distinct_signatures,
            "reference_match": self.reference_match,
            "notes": list(self.notes),
        }


@dataclass(slots=True)
class SensitivityAssessment:
    status: str
    reference_signature_count: int
    setting_signatures: list[SettingSignature]
    notes: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "reference_signature_count": self.reference_signature_count,
            "setting_signatures": [item.to_dict() for item in self.setting_signatures],
            "notes": list(self.notes),
        }


def _reference_signature_set(reference_signatures: list[dict[str, Any]]) -> set[str]:
    return {
        str(item.get("signature"))
        for item in reference_signatures
        if item.get("signature") is not None
    }


def classify_sensitivity_audit(
    *,
    reference_signatures: list[dict[str, Any]],
    setting_signatures: list[SettingSignature],
    supported_settings: list[SensitivitySetting],
    unsupported_notes: list[str] | None = None,
) -> SensitivityAssessment:
    reference_set = _reference_signature_set(reference_signatures)
    reference_count = len(reference_set)
    notes: list[str] = list(unsupported_notes or [])

    if not supported_settings:
        return SensitivityAssessment("inconclusive", reference_count, setting_signatures, notes + ["no supported settings"])
    if notes:
        return SensitivityAssessment("inconclusive", reference_count, setting_signatures, notes)

    distinct_counts = [item.distinct_signatures for item in setting_signatures]
    if not distinct_counts:
        return SensitivityAssessment("inconclusive", reference_count, setting_signatures, notes + ["no signatures recorded"])
    if any(count <= 0 for count in distinct_counts):
        return SensitivityAssessment("inconclusive", reference_count, setting_signatures, notes + ["insufficient evidence"])
    if any(item.distinct_signatures < reference_count for item in setting_signatures):
        if any(item.distinct_signatures <= 1 for item in setting_signatures):
            return SensitivityAssessment("collapse_worsened", reference_count, setting_signatures, notes + ["baseline signatures materially collapsed in at least one setting"])
        return SensitivityAssessment("fragile_collapse_reduced", reference_count, setting_signatures, notes + ["some settings reduced collapse, others degraded it"])
    if all(item.distinct_signatures == reference_count and item.reference_match for item in setting_signatures):
        return SensitivityAssessment("collapse_unchanged", reference_count, setting_signatures, notes + ["all supported settings matched the reference signature profile"])
    if all(item.distinct_signatures >= reference_count for item in setting_signatures):
        if any(item.distinct_signatures > reference_count for item in setting_signatures):
            return SensitivityAssessment("robust_collapse_reduced", reference_count, setting_signatures, notes + ["reduced collapse survived all supported settings and improved in at least one"])
        return SensitivityAssessment("collapse_unchanged", reference_count, setting_signatures, notes + ["all supported settings matched the reference diversity"])
    return SensitivityAssessment("inconclusive", reference_count, setting_signatures, notes + ["mixed or unsupported sensitivity pattern"])
