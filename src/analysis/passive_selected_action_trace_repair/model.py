from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class SelectedActionTraceSchemaSummary:
    required_fields: list[str]
    decision_point_fields: list[str]
    trace_source_fields: list[str]
    join_key_fields: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SelectedActionTraceEmissionSummary:
    selected_action_emitted_at_decision_point: bool
    selected_action_trace_source_emitted: bool
    selected_action_to_task_join_key_emitted: bool
    terminal_outcome_join_key_emitted: bool
    selected_action_metadata_emitted_after_outcome: bool
    selected_action_family_guessed_from_legality_mask: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SelectedActionFamilyTraceSummary:
    decision_opportunity_count: int | None
    selected_action_trace_record_count: int | None
    selected_action_family_trace_record_count: int | None
    selected_action_trace_coverage_ratio: float | None
    selected_action_family_coverage_ratio: float | None
    missing_selected_action_trace_count: int | None
    missing_selected_action_family_count: int | None
    selected_action_family_evidence_status: str
    selected_local_count: int | None
    selected_horizontal_count: int | None
    selected_vertical_count: int | None
    selected_action_count: int | None
    selected_action_count_consistency_verified: bool
    per_strategy_seed_selected_action_family_matrix: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SelectedActionToTaskJoinSummary:
    selected_action_to_task_join_count: int | None
    selected_action_to_task_join_coverage_ratio: float | None
    missing_selected_action_to_task_join_key_count: int | None
    selected_action_to_task_join_status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class TerminalOutcomeJoinKeySummary:
    terminal_outcome_join_key_count: int | None
    terminal_outcome_join_key_coverage_ratio: float | None
    missing_terminal_outcome_join_key_count: int | None
    terminal_outcome_join_status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class BehaviorEquivalenceSummary:
    checks: list[dict[str, Any]]
    passed: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class EvidenceReadinessForFeature050Rerun:
    evidence_readiness_for_feature_050_rerun: bool
    remaining_blockers: list[str]
    selected_action_family_evidence_status: str
    selected_action_to_task_join_status: str
    terminal_outcome_join_status: str
    per_action_outcome_join_readiness: str
    behavior_equivalence_passed: bool
    recommended_next_feature: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PassiveSelectedActionTraceRepairReport:
    feature_id: str
    prerequisite_tags_verified: list[dict[str, Any]]
    prior_feature_gates_verified: list[dict[str, Any]]
    decision_opportunity_count: int
    selected_action_trace_record_count: int
    selected_action_family_trace_record_count: int
    selected_action_to_task_join_key_count: int
    terminal_outcome_join_key_count: int
    selected_action_trace_coverage_ratio: float
    selected_action_family_coverage_ratio: float
    selected_action_to_task_join_coverage_ratio: float
    terminal_outcome_join_key_coverage_ratio: float
    missing_selected_action_trace_count: int
    missing_selected_action_family_count: int
    missing_selected_action_to_task_join_key_count: int
    missing_terminal_outcome_join_key_count: int
    behavior_equivalence_passed: bool
    selected_action_family_evidence_status: str
    selected_action_to_task_join_status: str
    terminal_outcome_join_status: str
    per_action_outcome_join_readiness: str
    selected_action_trace_schema: SelectedActionTraceSchemaSummary | dict[str, Any]
    selected_action_trace_emission_summary: SelectedActionTraceEmissionSummary | dict[str, Any]
    selected_action_family_trace_summary: SelectedActionFamilyTraceSummary | dict[str, Any]
    selected_action_to_task_join_summary: SelectedActionToTaskJoinSummary | dict[str, Any]
    terminal_outcome_join_key_summary: TerminalOutcomeJoinKeySummary | dict[str, Any]
    behavior_equivalence_summary: BehaviorEquivalenceSummary | dict[str, Any]
    evidence_readiness_for_feature_050_rerun: bool
    remaining_blockers: list[str]
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
        if self.behavior_equivalence_passed != self.behavior_equivalence_summary.passed:
            raise ValueError("behavior_equivalence_passed must match behavior_equivalence_summary.passed")
        if self.selected_action_family_evidence_status == "available":
            if not (self.decision_opportunity_count > 0 and self.selected_action_family_trace_record_count == self.decision_opportunity_count):
                raise ValueError("selected_action_family_evidence_status cannot be available without complete family trace records")
        if self.selected_action_to_task_join_status == "available":
            if not (self.selected_action_to_task_join_key_count == self.decision_opportunity_count and self.decision_opportunity_count > 0):
                raise ValueError("selected_action_to_task_join_status cannot be available without complete join keys")
        if self.terminal_outcome_join_status == "available":
            if not (self.terminal_outcome_join_key_count == self.decision_opportunity_count and self.decision_opportunity_count > 0):
                raise ValueError("terminal_outcome_join_status cannot be available without complete terminal join keys")
        if hasattr(self.selected_action_family_trace_summary, "selected_action_family_evidence_status"):
            if self.selected_action_family_evidence_status != self.selected_action_family_trace_summary.selected_action_family_evidence_status:
                raise ValueError("selected_action_family_evidence_status must match selected_action_family_trace_summary.selected_action_family_evidence_status")
        if hasattr(self.selected_action_to_task_join_summary, "selected_action_to_task_join_status"):
            if self.selected_action_to_task_join_status != self.selected_action_to_task_join_summary.selected_action_to_task_join_status:
                raise ValueError("selected_action_to_task_join_status must match selected_action_to_task_join_summary.selected_action_to_task_join_status")
        if hasattr(self.terminal_outcome_join_key_summary, "terminal_outcome_join_status"):
            if self.terminal_outcome_join_status != self.terminal_outcome_join_key_summary.terminal_outcome_join_status:
                raise ValueError("terminal_outcome_join_status must match terminal_outcome_join_key_summary.terminal_outcome_join_status")
        if self.evidence_readiness_for_feature_050_rerun:
            if self.selected_action_family_evidence_status != "available":
                raise ValueError("family status must be available when readiness is true")
            if self.selected_action_to_task_join_status != "available":
                raise ValueError("join status must be available when readiness is true")
            if self.terminal_outcome_join_status != "available":
                raise ValueError("terminal outcome status must be available when readiness is true")
            if self.per_action_outcome_join_readiness != "ready":
                raise ValueError("per_action_outcome_join_readiness must be ready when readiness is true")
            if not self.behavior_equivalence_summary.passed:
                raise ValueError("behavior equivalence must pass when readiness is true")
            if not self.no_action_selection_drift or not self.no_action_legality_drift:
                raise ValueError("no_action_selection_drift and no_action_legality_drift must be true when readiness is true")
            if self.final_verdict != "passive_selected_action_trace_ready_for_feature_050_rerun":
                raise ValueError("final verdict must match readiness")
        else:
            if not self.remaining_blockers:
                raise ValueError("remaining blockers required when readiness is false")

    def to_dict(self) -> dict[str, Any]:
        def serialize(value: Any) -> Any:
            return value.to_dict() if hasattr(value, "to_dict") else value

        return {
            "feature_id": self.feature_id,
            "prerequisite_tags_verified": list(self.prerequisite_tags_verified),
            "prior_feature_gates_verified": list(self.prior_feature_gates_verified),
            "decision_opportunity_count": self.decision_opportunity_count,
            "selected_action_trace_record_count": self.selected_action_trace_record_count,
            "selected_action_family_trace_record_count": self.selected_action_family_trace_record_count,
            "selected_action_to_task_join_key_count": self.selected_action_to_task_join_key_count,
            "terminal_outcome_join_key_count": self.terminal_outcome_join_key_count,
            "selected_action_trace_coverage_ratio": self.selected_action_trace_coverage_ratio,
            "selected_action_family_coverage_ratio": self.selected_action_family_coverage_ratio,
            "selected_action_to_task_join_coverage_ratio": self.selected_action_to_task_join_coverage_ratio,
            "terminal_outcome_join_key_coverage_ratio": self.terminal_outcome_join_key_coverage_ratio,
            "missing_selected_action_trace_count": self.missing_selected_action_trace_count,
            "missing_selected_action_family_count": self.missing_selected_action_family_count,
            "missing_selected_action_to_task_join_key_count": self.missing_selected_action_to_task_join_key_count,
            "missing_terminal_outcome_join_key_count": self.missing_terminal_outcome_join_key_count,
            "behavior_equivalence_passed": self.behavior_equivalence_passed,
            "selected_action_family_evidence_status": self.selected_action_family_evidence_status,
            "selected_action_to_task_join_status": self.selected_action_to_task_join_status,
            "terminal_outcome_join_status": self.terminal_outcome_join_status,
            "per_action_outcome_join_readiness": self.per_action_outcome_join_readiness,
            "selected_action_trace_schema": serialize(self.selected_action_trace_schema),
            "selected_action_trace_emission_summary": serialize(self.selected_action_trace_emission_summary),
            "selected_action_family_trace_summary": serialize(self.selected_action_family_trace_summary),
            "selected_action_to_task_join_summary": serialize(self.selected_action_to_task_join_summary),
            "terminal_outcome_join_key_summary": serialize(self.terminal_outcome_join_key_summary),
            "behavior_equivalence_summary": serialize(self.behavior_equivalence_summary),
            "evidence_readiness_for_feature_050_rerun": self.evidence_readiness_for_feature_050_rerun,
            "remaining_blockers": list(self.remaining_blockers),
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
