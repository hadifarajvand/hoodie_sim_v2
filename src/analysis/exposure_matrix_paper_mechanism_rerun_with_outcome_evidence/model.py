from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

ALLOWED_ALIGNMENT_STATUSES = ("available", "partial", "unavailable")
ALLOWED_FINAL_VERDICTS = (
    "paper_mechanism_alignment_ready_for_training_contract",
    "observation_vector_alignment_blocked",
    "formula_unit_alignment_blocked",
    "exposure_matrix_alignment_blocked",
    "selected_action_outcome_alignment_blocked",
    "behavior_drift_detected",
    "prerequisite_blocked",
)


def validate_alignment_status(value: str, field_name: str) -> str:
    if value not in ALLOWED_ALIGNMENT_STATUSES:
        raise ValueError(f"{field_name} must be one of {ALLOWED_ALIGNMENT_STATUSES}")
    return value


@dataclass(frozen=True, slots=True)
class BehaviorEquivalenceSummary:
    checks: list[dict[str, Any]]
    passed: bool

    def __post_init__(self) -> None:
        names = [str(check.get("name")) for check in self.checks]
        if len(names) != len(set(names)):
            raise ValueError("behavior-equivalence check names must be unique")
        if self.passed != all(bool(check.get("verified")) for check in self.checks):
            raise ValueError("behavior_equivalence_summary.passed must match the verification results")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ExposureMatrixPaperMechanismRerunReport:
    feature_id: str
    prerequisite_tags_verified: list[dict[str, Any]]
    prior_feature_gates_verified: list[dict[str, Any]]
    feature_052_trace_readiness_verified: bool
    feature_052_readiness_verified: bool
    observation_vector_alignment_status: str
    formula_unit_alignment_status: str
    exposure_matrix_alignment_status: str
    selected_action_outcome_alignment_status: str
    training_readiness_contract_status: str
    paper_mechanism_alignment_ready: bool
    remaining_blockers: list[str]
    recommended_next_feature: str
    behavior_equivalence_summary: BehaviorEquivalenceSummary | dict[str, Any]
    behavior_equivalence_passed: bool
    no_runtime_repair_performed: bool = True
    no_training_started: bool = True
    no_optimizer_step: bool = True
    no_replay_training: bool = True
    no_target_update_execution: bool = True
    no_checkpoint_written: bool = True
    no_checkpoint_generation: bool = True
    no_campaign_run: bool = True
    no_full_campaign: bool = True
    no_dependency_drift: bool = True
    no_dependency_changes: bool = True
    no_policy_drift: bool = True
    no_environment_drift: bool = True
    no_runtime_semantic_changes: bool = True
    no_prior_artifact_rewrite: bool = True
    no_paper_reproduction_claim: bool = True
    final_verdict: str = "prerequisite_blocked"

    def __post_init__(self) -> None:
        if self.feature_id != "053-exposure-matrix-paper-mechanism-rerun-with-outcome-evidence":
            raise ValueError("feature_id must equal Feature 053")
        for field_name in (
            "observation_vector_alignment_status",
            "formula_unit_alignment_status",
            "exposure_matrix_alignment_status",
            "selected_action_outcome_alignment_status",
            "training_readiness_contract_status",
        ):
            validate_alignment_status(getattr(self, field_name), field_name)
        summary_passed = self.behavior_equivalence_summary.passed if hasattr(self.behavior_equivalence_summary, "passed") else None
        if summary_passed is not None and self.behavior_equivalence_passed != summary_passed:
            raise ValueError("behavior_equivalence_passed must match behavior_equivalence_summary.passed")
        if self.final_verdict not in ALLOWED_FINAL_VERDICTS:
            raise ValueError("invalid final_verdict")
        if self.behavior_equivalence_passed and self.behavior_equivalence_summary.passed is False:
            raise ValueError("behavior_equivalence_passed cannot be true when the summary failed")
        if self.feature_052_trace_readiness_verified != self.feature_052_readiness_verified:
            raise ValueError("feature_052 readiness aliases must match")
        if self.paper_mechanism_alignment_ready:
            if self.final_verdict != "paper_mechanism_alignment_ready_for_training_contract":
                raise ValueError("ready reports must use the training-contract verdict")
            if self.recommended_next_feature != "Feature 054 — Training Readiness Contract":
                raise ValueError("ready reports must route to Feature 054")
            if self.remaining_blockers:
                raise ValueError("ready reports must not report blockers")
            for field_name in (
                "observation_vector_alignment_status",
                "formula_unit_alignment_status",
                "exposure_matrix_alignment_status",
                "selected_action_outcome_alignment_status",
                "training_readiness_contract_status",
            ):
                if getattr(self, field_name) != "available":
                    raise ValueError("ready reports require all alignment layers to be available")
        else:
            if self.final_verdict == "paper_mechanism_alignment_ready_for_training_contract":
                raise ValueError("unready reports cannot claim training-contract readiness")
            if not self.remaining_blockers:
                raise ValueError("unready reports must explain at least one blocker")
            if self.recommended_next_feature == "Feature 054 — Training Readiness Contract":
                raise ValueError("unready reports must not route to Feature 054")
        if not self.no_runtime_repair_performed:
            raise ValueError("no_runtime_repair_performed must remain true")
        for flag in (
            "no_training_started",
            "no_optimizer_step",
            "no_replay_training",
            "no_target_update_execution",
            "no_checkpoint_written",
            "no_checkpoint_generation",
            "no_campaign_run",
            "no_full_campaign",
            "no_dependency_drift",
            "no_dependency_changes",
            "no_policy_drift",
            "no_environment_drift",
            "no_runtime_semantic_changes",
            "no_prior_artifact_rewrite",
            "no_paper_reproduction_claim",
        ):
            if getattr(self, flag) is not True:
                raise ValueError(f"{flag} must remain true")

    def to_dict(self) -> dict[str, Any]:
        def serialize(value: Any) -> Any:
            return value.to_dict() if hasattr(value, "to_dict") else value

        return {
            "feature_id": self.feature_id,
            "prerequisite_tags_verified": list(self.prerequisite_tags_verified),
            "prior_feature_gates_verified": list(self.prior_feature_gates_verified),
            "feature_052_trace_readiness_verified": self.feature_052_trace_readiness_verified,
            "feature_052_readiness_verified": self.feature_052_readiness_verified,
            "observation_vector_alignment_status": self.observation_vector_alignment_status,
            "formula_unit_alignment_status": self.formula_unit_alignment_status,
            "exposure_matrix_alignment_status": self.exposure_matrix_alignment_status,
            "selected_action_outcome_alignment_status": self.selected_action_outcome_alignment_status,
            "training_readiness_contract_status": self.training_readiness_contract_status,
            "paper_mechanism_alignment_ready": self.paper_mechanism_alignment_ready,
            "remaining_blockers": list(self.remaining_blockers),
            "recommended_next_feature": self.recommended_next_feature,
            "behavior_equivalence_summary": serialize(self.behavior_equivalence_summary),
            "behavior_equivalence_passed": self.behavior_equivalence_passed,
            "no_runtime_repair_performed": self.no_runtime_repair_performed,
            "no_training_started": self.no_training_started,
            "no_optimizer_step": self.no_optimizer_step,
            "no_replay_training": self.no_replay_training,
            "no_target_update_execution": self.no_target_update_execution,
            "no_checkpoint_written": self.no_checkpoint_written,
            "no_checkpoint_generation": self.no_checkpoint_generation,
            "no_campaign_run": self.no_campaign_run,
            "no_full_campaign": self.no_full_campaign,
            "no_dependency_drift": self.no_dependency_drift,
            "no_dependency_changes": self.no_dependency_changes,
            "no_policy_drift": self.no_policy_drift,
            "no_environment_drift": self.no_environment_drift,
            "no_runtime_semantic_changes": self.no_runtime_semantic_changes,
            "no_prior_artifact_rewrite": self.no_prior_artifact_rewrite,
            "no_paper_reproduction_claim": self.no_paper_reproduction_claim,
            "final_verdict": self.final_verdict,
        }
