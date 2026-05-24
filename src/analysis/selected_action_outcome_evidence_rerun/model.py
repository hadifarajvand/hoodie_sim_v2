from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class SelectedActionFamilyEvidenceSummary:
    selected_local_count: int | None
    selected_horizontal_count: int | None
    selected_vertical_count: int | None
    selected_action_count: int | None
    selected_action_count_consistency_verified: bool
    per_strategy_seed_selected_action_family_matrix: list[dict[str, Any]]
    selected_action_family_evidence_status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SelectedActionToTaskJoinSummary:
    selected_action_to_task_join_count: int | None
    selected_action_to_task_join_ratio: float | None
    missing_selected_action_task_join_count: int | None
    selected_action_to_task_join_status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PerActionOutcomeJoinSummary:
    per_action_completion_count: dict[str, int | None]
    per_action_drop_count: dict[str, int | None]
    per_action_pending_count: dict[str, int | None]
    per_action_completion_rate: dict[str, float | None]
    per_action_drop_rate: dict[str, float | None]
    per_action_pending_rate: dict[str, float | None]
    per_action_outcome_evidence_status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PerActionOutcomeMatrix:
    per_strategy_seed_selected_action_family_matrix: list[dict[str, Any]]
    per_action_outcome_join_summary: PerActionOutcomeJoinSummary | dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "per_strategy_seed_selected_action_family_matrix": list(self.per_strategy_seed_selected_action_family_matrix),
            "per_action_outcome_join_summary": self.per_action_outcome_join_summary.to_dict() if hasattr(self.per_action_outcome_join_summary, "to_dict") else dict(self.per_action_outcome_join_summary),
        }


@dataclass(frozen=True, slots=True)
class LegalButUnselectedConsistencySummary:
    legal_but_unselected_local_count: int | None
    legal_but_unselected_horizontal_count: int | None
    legal_but_unselected_vertical_count: int | None
    legal_but_unselected_consistency_verified: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ExposureMatrixInternalConsistencySummary:
    selected_action_count_consistency_verified: bool
    selected_illegal_action_count: int | None
    selected_action_to_task_join_status: str
    per_action_outcome_evidence_status: str
    legal_but_unselected_consistency_verified: bool
    exposure_matrix_internal_consistency_verified: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class BehaviorEquivalenceSummary:
    checks: list[dict[str, Any]]
    passed: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Feature049UnblockAssessment:
    feature_049_can_be_rerun: bool
    feature_049_remaining_blockers: list[str]
    selected_action_family_evidence_status: str
    selected_action_to_task_join_status: str
    per_action_outcome_evidence_status: str
    legal_but_unselected_consistency_verified: bool
    exposure_matrix_internal_consistency_verified: bool
    behavior_equivalence_passed: bool
    recommended_next_feature: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class EvidencePopulationSummary:
    selected_action_trace_source: str
    selected_action_family_source: str
    selected_action_to_task_join_source: str
    terminal_outcome_join_source: str
    legal_count_source: str
    feature_051_source: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SelectedActionOutcomeEvidenceRerunReport:
    feature_id: str
    prerequisite_tags_verified: list[dict[str, Any]]
    prior_feature_gates_verified: list[dict[str, Any]]
    feature_051_trace_readiness_verified: bool
    selected_action_family_evidence_summary: SelectedActionFamilyEvidenceSummary | dict[str, Any]
    selected_action_to_task_join_summary: SelectedActionToTaskJoinSummary | dict[str, Any]
    per_action_outcome_join_summary: PerActionOutcomeJoinSummary | dict[str, Any]
    per_action_outcome_matrix: PerActionOutcomeMatrix | dict[str, Any]
    legal_but_unselected_consistency_summary: LegalButUnselectedConsistencySummary | dict[str, Any]
    exposure_matrix_internal_consistency_summary: ExposureMatrixInternalConsistencySummary | dict[str, Any]
    feature_049_unblock_assessment: Feature049UnblockAssessment | dict[str, Any]
    behavior_equivalence_summary: BehaviorEquivalenceSummary | dict[str, Any]
    evidence_population_summary: EvidencePopulationSummary | dict[str, Any]
    selected_action_family_evidence_status: str
    selected_action_to_task_join_status: str
    per_action_outcome_evidence_status: str
    behavior_equivalence_passed: bool
    feature_049_can_be_rerun: bool
    feature_049_remaining_blockers: list[str]
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
    final_verdict: str = "prerequisite_blocked"

    def __post_init__(self) -> None:
        summary_passed = self.behavior_equivalence_summary.passed if hasattr(self.behavior_equivalence_summary, "passed") else None
        if summary_passed is not None and self.behavior_equivalence_passed != summary_passed:
            raise ValueError("behavior_equivalence_passed must match behavior_equivalence_summary.passed")
        if self.selected_action_family_evidence_status not in {"available", "partial", "unavailable"}:
            raise ValueError("invalid selected_action_family_evidence_status")
        if self.selected_action_to_task_join_status not in {"available", "partial", "unavailable"}:
            raise ValueError("invalid selected_action_to_task_join_status")
        if self.per_action_outcome_evidence_status not in {"available", "partial", "unavailable"}:
            raise ValueError("invalid per_action_outcome_evidence_status")
        if self.feature_049_can_be_rerun and self.feature_049_remaining_blockers:
            raise ValueError("remaining blockers must be empty when rerun is allowed")
        if not self.feature_049_can_be_rerun and not self.feature_049_remaining_blockers:
            raise ValueError("remaining blockers required when rerun is blocked")

    def to_dict(self) -> dict[str, Any]:
        def serialize(value: Any) -> Any:
            return value.to_dict() if hasattr(value, "to_dict") else value

        return {
            "feature_id": self.feature_id,
            "prerequisite_tags_verified": list(self.prerequisite_tags_verified),
            "prior_feature_gates_verified": list(self.prior_feature_gates_verified),
            "feature_051_trace_readiness_verified": self.feature_051_trace_readiness_verified,
            "selected_action_family_evidence_summary": serialize(self.selected_action_family_evidence_summary),
            "selected_action_to_task_join_summary": serialize(self.selected_action_to_task_join_summary),
            "per_action_outcome_join_summary": serialize(self.per_action_outcome_join_summary),
            "per_action_outcome_matrix": serialize(self.per_action_outcome_matrix),
            "legal_but_unselected_consistency_summary": serialize(self.legal_but_unselected_consistency_summary),
            "exposure_matrix_internal_consistency_summary": serialize(self.exposure_matrix_internal_consistency_summary),
            "feature_049_unblock_assessment": serialize(self.feature_049_unblock_assessment),
            "behavior_equivalence_summary": serialize(self.behavior_equivalence_summary),
            "evidence_population_summary": serialize(self.evidence_population_summary),
            "selected_action_family_evidence_status": self.selected_action_family_evidence_status,
            "selected_action_to_task_join_status": self.selected_action_to_task_join_status,
            "per_action_outcome_evidence_status": self.per_action_outcome_evidence_status,
            "behavior_equivalence_passed": self.behavior_equivalence_passed,
            "feature_049_can_be_rerun": self.feature_049_can_be_rerun,
            "feature_049_remaining_blockers": list(self.feature_049_remaining_blockers),
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
