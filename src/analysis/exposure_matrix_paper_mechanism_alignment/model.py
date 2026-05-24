from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ExposureMatrixRerunSummary:
    decision_opportunity_count: int | None
    legal_local_count: int | None
    legal_horizontal_count: int | None
    legal_vertical_count: int | None
    selected_local_count: int | None
    selected_horizontal_count: int | None
    selected_vertical_count: int | None
    selected_illegal_action_count: int | None
    selected_illegal_action_rate: float | None
    legal_but_unselected_by_action: dict[str, int | None]
    per_action_completion_rate: dict[str, float | None]
    per_action_drop_rate: dict[str, float | None]
    per_action_pending_rate: dict[str, float | None]
    per_strategy_seed_matrix: list[dict[str, Any]]
    exposure_bias_summary: dict[str, Any]
    evidence_status: str
    selected_action_family_evidence_status: str
    selected_action_count_consistency_verified: bool
    legal_but_unselected_consistency_verified: bool
    per_action_outcome_evidence_status: str
    exposure_matrix_internal_consistency_verified: bool
    exposure_matrix_unblocked: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class LegalVsSelectedActionMatrix:
    matrix_complete: bool
    trace_backed: bool
    evidence_status: str
    supported_actions: list[str]
    rows: list[dict[str, Any]]
    summary: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ObservationVectorAudit:
    fields: dict[str, str]
    blocking_fields: list[str]
    passed: bool
    evidence_sources: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PaperFormulaUnitAudit:
    items: list[dict[str, Any]]
    passed: bool
    blocking_items: list[str]
    evidence_sources: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class TrainingReadinessDecision:
    readiness_state: str
    final_verdict: str
    recommended_next_feature: str
    rationale: str
    exposure_matrix_unblocked: bool
    observation_vector_audit_passed: bool
    paper_formula_unit_audit_passed: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ExposureMatrixPaperMechanismReport:
    feature_id: str
    prerequisite_tags_verified: list[dict[str, Any]]
    prior_feature_gates_verified: list[dict[str, Any]]
    legality_evidence_verified: dict[str, Any]
    exposure_matrix_rerun_summary: ExposureMatrixRerunSummary | dict[str, Any]
    legal_vs_selected_action_matrix: LegalVsSelectedActionMatrix | dict[str, Any]
    per_strategy_seed_matrix: list[dict[str, Any]]
    per_action_outcome_matrix: dict[str, Any]
    selected_illegal_action_summary: dict[str, Any]
    selected_action_family_evidence_status: str
    selected_action_count_consistency_verified: bool
    legal_but_unselected_consistency_verified: bool
    per_action_outcome_evidence_status: str
    exposure_matrix_internal_consistency_verified: bool
    observation_vector_audit: ObservationVectorAudit | dict[str, Any]
    paper_formula_unit_audit: PaperFormulaUnitAudit | dict[str, Any]
    runtime_semantic_drift_check: dict[str, Any]
    training_readiness_decision: TrainingReadinessDecision | dict[str, Any]
    recommended_next_feature: str
    no_runtime_repair_performed: bool = True
    no_training_started: bool = True
    no_optimizer_step: bool = True
    no_replay_training: bool = True
    no_target_update_execution: bool = True
    no_dependency_drift: bool = True
    no_policy_drift: bool = True
    no_reward_timing_change: bool = True
    no_timeout_contract_drift: bool = True
    no_capacity_contract_drift: bool = True
    no_transmission_contract_drift: bool = True
    no_action_legality_drift: bool = True
    no_action_selection_drift: bool = True
    no_curve_fitting: bool = True
    no_simulator_output_tuning: bool = True
    no_paper_reproduction_claim: bool = True
    final_verdict: str = "blocked_by_insufficient_evidence"

    def __post_init__(self) -> None:
        allowed = {
            "paper_mechanism_alignment_ready_for_training_contract",
            "observation_vector_gap_blocks_training",
            "formula_unit_gap_blocks_training",
            "exposure_bias_blocks_training",
            "runtime_semantic_contradiction_requires_repair",
            "insufficient_legality_or_trace_evidence",
            "prerequisite_blocked",
        }
        if self.final_verdict not in allowed:
            raise ValueError("invalid final_verdict")
        if self.final_verdict == "paper_mechanism_alignment_ready_for_training_contract" and self.recommended_next_feature != "Feature 050 — DDQN Training Contract Bundle":
            raise ValueError("ready verdict must recommend Feature 050")
        if self.final_verdict == "paper_mechanism_alignment_ready_for_training_contract":
            if self.selected_action_family_evidence_status != "available":
                raise ValueError("ready verdict requires selected action family evidence")
            if self.per_action_outcome_evidence_status != "available":
                raise ValueError("ready verdict requires per-action outcome evidence")
            if not self.exposure_matrix_internal_consistency_verified:
                raise ValueError("ready verdict requires internal consistency")
            if not self.selected_action_count_consistency_verified:
                raise ValueError("ready verdict requires selected action count consistency")
            if not self.legal_but_unselected_consistency_verified:
                raise ValueError("ready verdict requires legal-but-unselected consistency")
        if self.final_verdict == "observation_vector_gap_blocks_training" and self.recommended_next_feature != "observation vector implementation repair before training":
            raise ValueError("observation gap verdict must recommend observation repair")
        if self.final_verdict == "formula_unit_gap_blocks_training" and self.recommended_next_feature != "formula/unit repair before training":
            raise ValueError("formula gap verdict must recommend formula repair")
        if self.final_verdict == "exposure_bias_blocks_training" and self.recommended_next_feature != "observation vector/action exposure repair before training":
            raise ValueError("exposure bias verdict must recommend exposure repair")
        if self.final_verdict == "runtime_semantic_contradiction_requires_repair" and self.recommended_next_feature != "runtime semantic repair before training":
            raise ValueError("runtime semantic verdict must recommend runtime repair")
        if self.final_verdict == "insufficient_legality_or_trace_evidence" and self.recommended_next_feature not in {
            "trace/evidence expansion before training",
            "selected-action family evidence expansion before training",
            "per-action outcome evidence expansion before training",
        }:
            raise ValueError("insufficient evidence verdict must recommend an evidence expansion path")
        if self.final_verdict == "prerequisite_blocked" and not self.recommended_next_feature:
            raise ValueError("prerequisite blocked requires next feature guidance")
        if self.final_verdict != "paper_mechanism_alignment_ready_for_training_contract" and self.recommended_next_feature == "Feature 050 — DDQN Training Contract Bundle":
            raise ValueError("Feature 050 cannot be recommended unless readiness is achieved")
        for flag in (
            "no_runtime_repair_performed",
            "no_training_started",
            "no_optimizer_step",
            "no_replay_training",
            "no_target_update_execution",
            "no_dependency_drift",
            "no_policy_drift",
            "no_reward_timing_change",
            "no_timeout_contract_drift",
            "no_capacity_contract_drift",
            "no_transmission_contract_drift",
            "no_action_legality_drift",
            "no_action_selection_drift",
            "no_curve_fitting",
            "no_simulator_output_tuning",
            "no_paper_reproduction_claim",
        ):
            if getattr(self, flag) is not True:
                raise ValueError(f"{flag} must be true")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "prerequisite_tags_verified": list(self.prerequisite_tags_verified),
            "prior_feature_gates_verified": list(self.prior_feature_gates_verified),
            "legality_evidence_verified": dict(self.legality_evidence_verified),
            "exposure_matrix_rerun_summary": self.exposure_matrix_rerun_summary.to_dict() if hasattr(self.exposure_matrix_rerun_summary, "to_dict") else dict(self.exposure_matrix_rerun_summary),
            "legal_vs_selected_action_matrix": self.legal_vs_selected_action_matrix.to_dict() if hasattr(self.legal_vs_selected_action_matrix, "to_dict") else dict(self.legal_vs_selected_action_matrix),
            "per_strategy_seed_matrix": list(self.per_strategy_seed_matrix),
            "per_action_outcome_matrix": dict(self.per_action_outcome_matrix),
            "selected_illegal_action_summary": dict(self.selected_illegal_action_summary),
            "selected_action_family_evidence_status": self.selected_action_family_evidence_status,
            "selected_action_count_consistency_verified": self.selected_action_count_consistency_verified,
            "legal_but_unselected_consistency_verified": self.legal_but_unselected_consistency_verified,
            "per_action_outcome_evidence_status": self.per_action_outcome_evidence_status,
            "exposure_matrix_internal_consistency_verified": self.exposure_matrix_internal_consistency_verified,
            "observation_vector_audit": self.observation_vector_audit.to_dict() if hasattr(self.observation_vector_audit, "to_dict") else dict(self.observation_vector_audit),
            "paper_formula_unit_audit": self.paper_formula_unit_audit.to_dict() if hasattr(self.paper_formula_unit_audit, "to_dict") else dict(self.paper_formula_unit_audit),
            "runtime_semantic_drift_check": dict(self.runtime_semantic_drift_check),
            "training_readiness_decision": self.training_readiness_decision.to_dict() if hasattr(self.training_readiness_decision, "to_dict") else dict(self.training_readiness_decision),
            "recommended_next_feature": self.recommended_next_feature,
            "no_runtime_repair_performed": self.no_runtime_repair_performed,
            "no_training_started": self.no_training_started,
            "no_optimizer_step": self.no_optimizer_step,
            "no_replay_training": self.no_replay_training,
            "no_target_update_execution": self.no_target_update_execution,
            "no_dependency_drift": self.no_dependency_drift,
            "no_policy_drift": self.no_policy_drift,
            "no_reward_timing_change": self.no_reward_timing_change,
            "no_timeout_contract_drift": self.no_timeout_contract_drift,
            "no_capacity_contract_drift": self.no_capacity_contract_drift,
            "no_transmission_contract_drift": self.no_transmission_contract_drift,
            "no_action_legality_drift": self.no_action_legality_drift,
            "no_action_selection_drift": self.no_action_selection_drift,
            "no_curve_fitting": self.no_curve_fitting,
            "no_simulator_output_tuning": self.no_simulator_output_tuning,
            "no_paper_reproduction_claim": self.no_paper_reproduction_claim,
            "final_verdict": self.final_verdict,
        }
