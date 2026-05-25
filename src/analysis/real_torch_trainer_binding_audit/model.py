from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .config import FEATURE_ID, READY_NEXT_FEATURE, REPAIR_NEXT_FEATURE

ALLOWED_FINAL_VERDICTS = (
    "real_torch_trainer_binding_verified",
    "real_torch_trainer_binding_missing_repair_required",
    "torch_environment_blocked",
    "feature_060_artifact_missing",
    "feature_060_code_missing",
    "audit_scope_blocked",
)

REPAIR_ROUTING = {
    "real_torch_trainer_binding_missing_repair_required": REPAIR_NEXT_FEATURE,
    "torch_environment_blocked": "Repair Feature 060A Torch/TorchRL environment evidence",
    "feature_060_artifact_missing": "Repair Feature 060 campaign artifact availability before binding audit",
    "feature_060_code_missing": "Repair Feature 060 source availability before binding audit",
    "audit_scope_blocked": "Repair Feature 060A audit scope hygiene",
}

PYTHON_ENVIRONMENT_KEYS = (
    "which_python3",
    "sys_executable",
    "same_interpreter_expected",
)
TORCH_AVAILABILITY_KEYS = (
    "torch_find_spec_available",
    "torchrl_find_spec_available",
    "torch_import_available",
    "torch_version",
    "torch_pip_show_present",
    "torchrl_pip_show_present",
)
FEATURE_060_CLAIM_KEYS = (
    "feature_060_report_exists",
    "feature_060_final_verdict",
    "feature_060_recommended_next_feature",
    "feature_060_remaining_blockers",
    "feature_060_claims_campaign_execution_passed",
)
FEATURE_060_BINDING_KEYS = (
    "runner_imports_torch",
    "runner_imports_torchrl",
    "runner_imports_real_trainer_candidate",
    "runner_instantiates_real_trainer_candidate",
    "runner_executes_real_trainer_update_or_fit",
    "runner_uses_scalar_fallback_campaign",
)
BINDING_AUDIT_KEYS = (
    "environment_supports_real_binding",
    "real_binding_verified",
    "feature_060_claim_supported",
    "repair_required",
    "repair_feature",
)


def _required_keys(summary: dict[str, Any], field_name: str, keys: tuple[str, ...]) -> None:
    missing = [key for key in keys if key not in summary]
    if missing:
        raise ValueError(f"{field_name} is missing required keys: {missing}")


def _ensure_unique_names(entries: list[dict[str, Any]], field_name: str) -> None:
    names = [str(entry.get("name")) for entry in entries]
    if len(names) != len(set(names)):
        raise ValueError(f"{field_name} names must be unique")


@dataclass(frozen=True, slots=True)
class RealTorchTrainerBindingAuditReport:
    feature_id: str
    prerequisite_tags_verified: list[dict[str, Any]]
    python_environment_summary: dict[str, Any]
    torch_availability_summary: dict[str, Any]
    feature_060_claim_summary: dict[str, Any]
    feature_060_code_binding_summary: dict[str, Any]
    real_trainer_candidate_summary: dict[str, Any]
    simulation_fallback_summary: dict[str, Any]
    binding_audit_summary: dict[str, Any]
    remaining_blockers: list[str] = field(default_factory=list)
    recommended_next_feature: str = ""
    final_verdict: str = "real_torch_trainer_binding_missing_repair_required"

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 060a-real-torch-trainer-binding-audit")
        if self.final_verdict not in ALLOWED_FINAL_VERDICTS:
            raise ValueError(f"invalid final_verdict: {self.final_verdict}")

        _ensure_unique_names(self.prerequisite_tags_verified, "prerequisite_tags_verified")
        for entry in self.prerequisite_tags_verified:
            if not isinstance(entry.get("verified"), bool):
                raise ValueError(f"prerequisite_tags_verified.{entry.get('name')}.verified must be boolean")

        _required_keys(self.python_environment_summary, "python_environment_summary", PYTHON_ENVIRONMENT_KEYS)
        _required_keys(self.torch_availability_summary, "torch_availability_summary", TORCH_AVAILABILITY_KEYS)
        _required_keys(self.feature_060_claim_summary, "feature_060_claim_summary", FEATURE_060_CLAIM_KEYS)
        _required_keys(self.feature_060_code_binding_summary, "feature_060_code_binding_summary", FEATURE_060_BINDING_KEYS)
        _required_keys(self.binding_audit_summary, "binding_audit_summary", BINDING_AUDIT_KEYS)
        _required_keys(
            self.real_trainer_candidate_summary,
            "real_trainer_candidate_summary",
            ("candidate_count", "candidates", "feature_060_referenced_candidate_names"),
        )
        _required_keys(
            self.simulation_fallback_summary,
            "simulation_fallback_summary",
            (
                "random_random_used",
                "manual_replay_list_construction",
                "manual_scalar_loss_calculation",
                "manual_optimizer_step_count_increment",
                "manual_target_sync_count_calculation",
                "torch_tensor_module_optimizer_absent",
                "scalar_fallback_detected",
            ),
        )

        if self.final_verdict == "real_torch_trainer_binding_verified":
            if self.remaining_blockers:
                raise ValueError("verified verdict cannot include remaining_blockers")
            if self.recommended_next_feature != READY_NEXT_FEATURE:
                raise ValueError("verified verdict must route to Feature 061")
            if self.binding_audit_summary.get("real_binding_verified") is not True:
                raise ValueError("verified verdict requires real_binding_verified true")
            if self.binding_audit_summary.get("feature_060_claim_supported") is not True:
                raise ValueError("verified verdict requires Feature 060 claim support")
        else:
            if not self.remaining_blockers:
                raise ValueError("blocked or repair verdict must include remaining_blockers")
            expected_next = REPAIR_ROUTING[self.final_verdict]
            if self.recommended_next_feature != expected_next:
                raise ValueError(f"{self.final_verdict} must route to {expected_next}")

        if (
            self.feature_060_claim_summary.get("feature_060_claims_campaign_execution_passed") is True
            and self.binding_audit_summary.get("real_binding_verified") is not True
            and self.final_verdict == "real_torch_trainer_binding_verified"
        ):
            raise ValueError("Feature 060 pass claim cannot be supported without real binding")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
