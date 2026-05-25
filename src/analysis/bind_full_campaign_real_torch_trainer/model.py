from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .config import FEATURE_ID, READY_NEXT_FEATURE

ALLOWED_FINAL_VERDICTS = (
    "real_torch_trainer_binding_repair_passed",
    "feature_060a_prerequisite_blocked",
    "torch_environment_blocked",
    "real_trainer_binding_blocked",
    "feature_060_repair_blocked",
    "artifact_regeneration_blocked",
    "behavior_drift_detected",
)

REPAIR_ROUTING = {
    "feature_060a_prerequisite_blocked": "Repair Feature 060A audit prerequisite before Feature 060B can proceed",
    "torch_environment_blocked": "Repair repo venv Torch/TorchRL availability before Feature 060B can proceed",
    "real_trainer_binding_blocked": "Repair Feature 060 real trainer import/instantiation/update binding",
    "feature_060_repair_blocked": "Repair regenerated Feature 060 report claim support",
    "artifact_regeneration_blocked": "Repair Feature 060 artifact regeneration",
    "behavior_drift_detected": "Repair Feature 060B behavior/scope guard",
}


def _required_keys(summary: dict[str, Any], field_name: str, keys: tuple[str, ...]) -> None:
    missing = [key for key in keys if key not in summary]
    if missing:
        raise ValueError(f"{field_name} missing keys: {missing}")


def _unique_names(entries: list[dict[str, Any]]) -> None:
    names = [str(entry.get("name")) for entry in entries]
    if len(names) != len(set(names)):
        raise ValueError("prerequisite tag names must be unique")


@dataclass(frozen=True, slots=True)
class BindFullCampaignRealTorchTrainerReport:
    feature_id: str
    prerequisite_tags_verified: list[dict[str, Any]]
    feature_060a_audit_verified: bool
    torch_environment_summary: dict[str, Any]
    real_trainer_binding_summary: dict[str, Any]
    feature_060_repair_summary: dict[str, Any]
    campaign_execution_summary: dict[str, Any]
    training_metrics_summary: dict[str, Any]
    evaluation_metrics_summary: dict[str, Any]
    artifact_regeneration_summary: dict[str, Any]
    safety_summary: dict[str, Any]
    remaining_blockers: list[str] = field(default_factory=list)
    recommended_next_feature: str = ""
    final_verdict: str = "feature_060_repair_blocked"

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 060b-bind-full-campaign-real-torch-trainer")
        if self.final_verdict not in ALLOWED_FINAL_VERDICTS:
            raise ValueError("invalid final_verdict")
        _unique_names(self.prerequisite_tags_verified)
        for entry in self.prerequisite_tags_verified:
            if not isinstance(entry.get("verified"), bool):
                raise ValueError(f"prerequisite tag {entry.get('name')} verified must be boolean")
        _required_keys(self.torch_environment_summary, "torch_environment_summary", ("repo_venv_python", "torch_available", "torchrl_available", "torch_version"))
        _required_keys(
            self.real_trainer_binding_summary,
            "real_trainer_binding_summary",
            (
                "real_binding_verified",
                "torch_import_used",
                "torchrl_available",
                "real_trainer_import_used",
                "real_trainer_instantiated",
                "real_trainer_update_or_train_called",
                "scalar_fallback_drives_campaign_claim",
            ),
        )
        _required_keys(self.feature_060_repair_summary, "feature_060_repair_summary", ("feature_060_claim_supported", "feature_060_final_verdict", "feature_060_remaining_blockers"))
        _required_keys(self.artifact_regeneration_summary, "artifact_regeneration_summary", ("all_regenerated_artifacts_exist", "artifact_exists"))
        if self.final_verdict == "real_torch_trainer_binding_repair_passed":
            if self.remaining_blockers:
                raise ValueError("passing report cannot include blockers")
            if self.recommended_next_feature != READY_NEXT_FEATURE:
                raise ValueError("passing report must route to Feature 061")
            if self.feature_060a_audit_verified is not True:
                raise ValueError("passing report requires Feature 060A audit verification")
            if self.real_trainer_binding_summary.get("real_binding_verified") is not True:
                raise ValueError("passing report requires real binding")
            if self.feature_060_repair_summary.get("feature_060_claim_supported") is not True:
                raise ValueError("passing report requires Feature 060 claim support")
        else:
            if not self.remaining_blockers:
                raise ValueError("blocked report must include blockers")
            if self.recommended_next_feature == READY_NEXT_FEATURE:
                raise ValueError("blocked report must not route to Feature 061")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
