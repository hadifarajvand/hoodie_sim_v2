from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


SUPPORTED_ACTIONS = ("local", "horizontal", "vertical")


@dataclass(frozen=True, slots=True)
class LegalitySnapshot:
    strategy: str
    seed: int
    slot: int
    agent_id: str | int | None
    task_id: str | int | None
    selected_action: str | None
    action_index: int | None
    legal_local: bool | None
    legal_horizontal: bool | None
    legal_vertical: bool | None
    legal_action_mask: dict[str, bool]
    selected_was_legal: bool | None
    selected_illegal_reason: str | None
    legal_horizontal_neighbors: list[str]
    horizontal_neighbor_count: int | None
    vertical_available: bool | None
    cloud_available: bool | None
    private_queue_available: bool | None
    public_queue_available: bool | None
    legality_evidence_source: str
    legality_snapshot_schema_version: int = 1

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class LegalityEvidenceRecord:
    strategy: str
    seed: int
    snapshot: LegalitySnapshot
    selected_action_count: int | None
    selected_illegal_action_count: int | None
    selected_illegal_local_count: int | None
    selected_illegal_horizontal_count: int | None
    selected_illegal_vertical_count: int | None
    selected_illegal_action_rate: float | None
    selected_illegal_action_examples: list[dict[str, Any]] = field(default_factory=list)
    selected_illegal_action_evidence_status: str = "available"
    decision_opportunity_count: int | None = None
    legality_snapshot_count: int | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["snapshot"] = self.snapshot.to_dict()
        return payload


@dataclass(frozen=True, slots=True)
class BehaviorEquivalenceCheck:
    name: str
    verified: bool
    details: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class LegalityEvidenceCollector:
    snapshots: list[LegalitySnapshot]
    decision_opportunity_count: int | None
    legality_snapshot_count: int | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_opportunity_count": self.decision_opportunity_count,
            "legality_snapshot_count": self.legality_snapshot_count,
            "snapshots": [snapshot.to_dict() for snapshot in self.snapshots],
        }


@dataclass(frozen=True, slots=True)
class LegalityEvidenceReport:
    feature_id: str
    prerequisite_tags_verified: list[dict[str, Any]]
    prior_feature_gates_verified: list[dict[str, Any]]
    paper_default_runtime_verified: dict[str, Any]
    legality_evidence_source: str
    legality_snapshot_schema: dict[str, Any]
    legal_evidence_coverage_ratio: float | None
    legality_evidence_coverage_summary: dict[str, Any]
    per_strategy_seed_legality_coverage: list[dict[str, Any]]
    action_mask_summary: dict[str, Any]
    selected_illegal_action_summary: dict[str, Any]
    selected_illegal_action_count: int | None
    selected_illegal_local_count: int | None
    selected_illegal_horizontal_count: int | None
    selected_illegal_vertical_count: int | None
    selected_illegal_action_rate: float | None
    selected_illegal_action_examples: list[dict[str, Any]]
    selected_illegal_action_evidence_status: str
    behavior_equivalence_summary: dict[str, Any]
    exposure_matrix_unblocked: bool
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
        if "legal_evidence_coverage_ratio" not in self.legality_evidence_coverage_summary:
            raise ValueError("legality_evidence_coverage_summary.legal_evidence_coverage_ratio is required.")
        if self.legal_evidence_coverage_ratio != self.legality_evidence_coverage_summary.get("legal_evidence_coverage_ratio"):
            raise ValueError("Top-level and nested legal_evidence_coverage_ratio values must match.")
        decision_opportunity_count = self.legality_evidence_coverage_summary.get("decision_opportunity_count")
        if self.legal_evidence_coverage_ratio is None and decision_opportunity_count not in (0, None):
            raise ValueError("legal_evidence_coverage_ratio may only be null when decision_opportunity_count is zero or unavailable.")
        if self.legal_evidence_coverage_ratio is not None and self.legal_evidence_coverage_ratio < 0:
            raise ValueError("legal_evidence_coverage_ratio cannot be negative.")
        if self.final_verdict not in {
            "legality_evidence_ready_for_exposure_matrix_rerun",
            "legality_evidence_partial_requires_trace_depth_expansion",
            "legality_evidence_unavailable_requires_runtime_public_helper",
            "behavior_drift_detected",
            "prerequisite_blocked",
        }:
            raise ValueError("Invalid final_verdict.")
        behavior_passed = self.behavior_equivalence_summary.get("passed") is True
        if not behavior_passed:
            if self.final_verdict != "behavior_drift_detected":
                raise ValueError("Behavior drift must route to behavior_drift_detected.")
            if self.recommended_next_feature == "Feature 049 - Exposure-Matrix Rerun with Legality Evidence":
                raise ValueError("Behavior drift must not recommend Feature 049.")
        elif self.legal_evidence_coverage_ratio in (0.0, None):
            if self.final_verdict != "legality_evidence_unavailable_requires_runtime_public_helper":
                raise ValueError("Zero/null legality coverage must route to the public-helper verdict.")
            if self.recommended_next_feature != "public legality helper feature before exposure-matrix rerun":
                raise ValueError("Zero/null legality coverage must recommend the public legality helper feature.")
        elif 0.0 < self.legal_evidence_coverage_ratio < 1.0:
            if self.final_verdict != "legality_evidence_partial_requires_trace_depth_expansion":
                raise ValueError("Partial legality coverage must route to trace-depth expansion.")
            if self.recommended_next_feature != "trace-depth expansion before exposure-matrix rerun":
                raise ValueError("Partial legality coverage must recommend trace-depth expansion.")
        else:
            if self.final_verdict != "legality_evidence_ready_for_exposure_matrix_rerun":
                raise ValueError("Full legality coverage with passing behavior equivalence must route to Feature 049.")
            if self.recommended_next_feature != "Feature 049 - Exposure-Matrix Rerun with Legality Evidence":
                raise ValueError("Full legality coverage with passing behavior equivalence must recommend Feature 049.")
            if not self.exposure_matrix_unblocked:
                raise ValueError("Exposure matrix cannot be blocked when final_verdict says it is ready.")
        if self.selected_illegal_action_evidence_status == "unavailable":
            if self.selected_illegal_action_count is not None:
                raise ValueError("Unavailable legality evidence must not report a selected_illegal_action_count.")
            if self.selected_illegal_action_rate is not None:
                raise ValueError("Unavailable legality evidence must not report a selected_illegal_action_rate.")
            if self.selected_illegal_action_examples:
                raise ValueError("Unavailable legality evidence must not report selected_illegal_action_examples.")
        elif self.selected_illegal_action_count is None:
            raise ValueError("Available legality evidence must report selected_illegal_action_count.")
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
                raise ValueError(f"{flag} must be true.")

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "feature_id": self.feature_id,
            "prerequisite_tags_verified": list(self.prerequisite_tags_verified),
            "prior_feature_gates_verified": list(self.prior_feature_gates_verified),
            "paper_default_runtime_verified": dict(self.paper_default_runtime_verified),
            "legality_evidence_source": self.legality_evidence_source,
            "legality_snapshot_schema": dict(self.legality_snapshot_schema),
            "legal_evidence_coverage_ratio": self.legal_evidence_coverage_ratio,
            "legality_evidence_coverage_summary": dict(self.legality_evidence_coverage_summary),
            "per_strategy_seed_legality_coverage": list(self.per_strategy_seed_legality_coverage),
            "action_mask_summary": dict(self.action_mask_summary),
            "selected_illegal_action_summary": dict(self.selected_illegal_action_summary),
            "selected_illegal_action_count": self.selected_illegal_action_count,
            "selected_illegal_local_count": self.selected_illegal_local_count,
            "selected_illegal_horizontal_count": self.selected_illegal_horizontal_count,
            "selected_illegal_vertical_count": self.selected_illegal_vertical_count,
            "selected_illegal_action_rate": self.selected_illegal_action_rate,
            "selected_illegal_action_examples": list(self.selected_illegal_action_examples),
            "selected_illegal_action_evidence_status": self.selected_illegal_action_evidence_status,
            "behavior_equivalence_summary": dict(self.behavior_equivalence_summary),
            "exposure_matrix_unblocked": self.exposure_matrix_unblocked,
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
        payload["legality_evidence_coverage_summary"] = dict(self.legality_evidence_coverage_summary)
        return payload
