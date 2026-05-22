from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any

SUPPORTED_ACTIONS = ("local", "horizontal", "vertical")


@dataclass(frozen=True, slots=True)
class ExposureDecisionRecord:
    run_id: str
    strategy: str
    seed: int
    decision_opportunity_index: int
    generated_task_id: str | int | None
    admitted_slot: int | None
    selected_action: str | None
    legal_local: bool | None
    legal_horizontal: bool | None
    legal_vertical: bool | None
    selected_was_legal: bool | None
    destination: str | None
    queue_type: str | None
    terminal_outcome: str | None
    reward_available: bool | None
    pending_at_horizon: bool | None
    task_age_slots: int | None
    wait_slots: int | None
    execution_progress_slots: int | None
    transmission_delay_slots: int | None
    evidence_source: str
    selected_action_available: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ExposureMatrixMetrics:
    evidence_population: str
    decision_opportunity_count: int | None
    generated_task_count: int | None
    admitted_task_count: int | None
    selected_action_count: int | None
    terminal_task_count: int | None
    completed_task_count: int | None
    dropped_task_count: int | None
    pending_at_horizon_count: int | None
    legal_local_count: int | None
    legal_horizontal_count: int | None
    legal_vertical_count: int | None
    selected_local_count: int | None
    selected_horizontal_count: int | None
    selected_vertical_count: int | None
    selected_illegal_local_count: int | None
    selected_illegal_horizontal_count: int | None
    selected_illegal_vertical_count: int | None
    legal_but_unselected_local_count: int | None
    legal_but_unselected_horizontal_count: int | None
    legal_but_unselected_vertical_count: int | None
    selected_illegal_action_count: int | None
    selected_illegal_action_examples: list[dict[str, Any]]
    selected_illegal_action_rate: float | None
    action_entropy: float | None
    per_action_completion_rate: dict[str, float | None]
    per_action_drop_rate: dict[str, float | None]
    per_action_pending_rate: dict[str, float | None]
    per_action_mean_wait_slots: dict[str, float | None]
    per_action_mean_execution_progress_slots: dict[str, float | None]
    per_action_mean_task_age_at_terminal: dict[str, float | None]
    private_queue_admission_count: int | None
    public_queue_admission_count: int | None
    cloud_queue_admission_count: int | None
    offloaded_transmission_started_count: int | None
    offloaded_transmission_completed_count: int | None
    offloaded_completed_count: int | None
    offloaded_dropped_count: int | None
    offloaded_pending_count: int | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class IllegalActionSummary:
    selected_illegal_action_count: int | None
    selected_illegal_local_count: int | None
    selected_illegal_horizontal_count: int | None
    selected_illegal_vertical_count: int | None
    selected_illegal_action_examples: list[dict[str, Any]]
    selected_illegal_action_rate: float | None
    evidence_status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ExposureMatrixReport:
    feature_id: str
    prerequisite_tags_verified: list[dict[str, Any]]
    prior_feature_gates_verified: list[dict[str, Any]]
    paper_default_runtime_verified: dict[str, Any]
    exposure_matrix_input_sources: list[dict[str, Any]]
    exposure_matrix_population: str
    legal_action_evidence_source: str
    legal_action_evidence_coverage_ratio: float | None
    per_strategy_seed_matrix: list[dict[str, Any]]
    aggregate_exposure_matrix: dict[str, Any]
    per_action_outcome_matrix: dict[str, Any]
    per_queue_matrix: dict[str, Any]
    offload_exposure_matrix: dict[str, Any]
    illegal_action_summary: IllegalActionSummary | dict[str, Any]
    exposure_bias_summary: dict[str, Any]
    load_vs_exposure_summary: dict[str, Any]
    matrix_completeness_summary: dict[str, Any]
    dominant_exposure_findings: list[dict[str, Any]]
    diagnosis: dict[str, Any]
    recommended_next_feature: str
    no_runtime_repair_performed: bool = True
    no_training_started: bool = True
    no_optimizer_step: bool = True
    no_replay_training: bool = True
    no_target_update_execution: bool = True
    no_dependency_drift: bool = True
    no_environment_contract_drift: bool = True
    no_policy_drift: bool = True
    no_reward_timing_change: bool = True
    no_timeout_contract_drift: bool = True
    no_capacity_contract_drift: bool = True
    no_transmission_contract_drift: bool = True
    no_action_legality_drift: bool = True
    no_curve_fitting: bool = True
    no_simulator_output_tuning: bool = True
    no_paper_reproduction_claim: bool = True
    final_verdict: str = "prerequisite_blocked"

    def to_dict(self) -> dict[str, Any]:
        illegal = self.illegal_action_summary.to_dict() if hasattr(self.illegal_action_summary, "to_dict") else dict(self.illegal_action_summary)
        return {
            "feature_id": self.feature_id,
            "prerequisite_tags_verified": list(self.prerequisite_tags_verified),
            "prior_feature_gates_verified": list(self.prior_feature_gates_verified),
            "paper_default_runtime_verified": dict(self.paper_default_runtime_verified),
            "exposure_matrix_input_sources": list(self.exposure_matrix_input_sources),
            "exposure_matrix_population": self.exposure_matrix_population,
            "legal_action_evidence_source": self.legal_action_evidence_source,
            "legal_action_evidence_coverage_ratio": self.legal_action_evidence_coverage_ratio,
            "per_strategy_seed_matrix": list(self.per_strategy_seed_matrix),
            "aggregate_exposure_matrix": dict(self.aggregate_exposure_matrix),
            "per_action_outcome_matrix": dict(self.per_action_outcome_matrix),
            "per_queue_matrix": dict(self.per_queue_matrix),
            "offload_exposure_matrix": dict(self.offload_exposure_matrix),
            "illegal_action_summary": illegal,
            "exposure_bias_summary": dict(self.exposure_bias_summary),
            "load_vs_exposure_summary": dict(self.load_vs_exposure_summary),
            "matrix_completeness_summary": dict(self.matrix_completeness_summary),
            "dominant_exposure_findings": list(self.dominant_exposure_findings),
            "diagnosis": dict(self.diagnosis),
            "recommended_next_feature": self.recommended_next_feature,
            "no_runtime_repair_performed": self.no_runtime_repair_performed,
            "no_training_started": self.no_training_started,
            "no_optimizer_step": self.no_optimizer_step,
            "no_replay_training": self.no_replay_training,
            "no_target_update_execution": self.no_target_update_execution,
            "no_dependency_drift": self.no_dependency_drift,
            "no_environment_contract_drift": self.no_environment_contract_drift,
            "no_policy_drift": self.no_policy_drift,
            "no_reward_timing_change": self.no_reward_timing_change,
            "no_timeout_contract_drift": self.no_timeout_contract_drift,
            "no_capacity_contract_drift": self.no_capacity_contract_drift,
            "no_transmission_contract_drift": self.no_transmission_contract_drift,
            "no_action_legality_drift": self.no_action_legality_drift,
            "no_curve_fitting": self.no_curve_fitting,
            "no_simulator_output_tuning": self.no_simulator_output_tuning,
            "no_paper_reproduction_claim": self.no_paper_reproduction_claim,
            "final_verdict": self.final_verdict,
        }


def selected_action_is_illegal(record: ExposureDecisionRecord) -> tuple[bool | None, str | None]:
    if record.selected_action is None:
        if record.selected_action_available:
            return True, "missing selected_action"
        return None, None
    if record.selected_action not in SUPPORTED_ACTIONS:
        return True, "unsupported selected_action"
    if record.selected_action == "local":
        return (record.legal_local is False, "legal_local is false" if record.legal_local is False else None)
    if record.selected_action == "horizontal":
        return (record.legal_horizontal is False, "legal_horizontal is false" if record.legal_horizontal is False else None)
    if record.selected_action == "vertical":
        return (record.legal_vertical is False, "legal_vertical is false" if record.legal_vertical is False else None)
    return True, "unsupported selected_action"


def build_illegal_action_summary(
    records: list[ExposureDecisionRecord],
    legal_evidence_available: bool,
) -> IllegalActionSummary:
    if not legal_evidence_available:
        return IllegalActionSummary(
            selected_illegal_action_count=None,
            selected_illegal_local_count=None,
            selected_illegal_horizontal_count=None,
            selected_illegal_vertical_count=None,
            selected_illegal_action_examples=[],
            selected_illegal_action_rate=None,
            evidence_status="unavailable",
        )

    total = 0
    local = 0
    horizontal = 0
    vertical = 0
    examples: list[dict[str, Any]] = []
    selected_action_count = 0
    for record in records:
        if record.selected_action_available:
            selected_action_count += 1
        illegal, reason = selected_action_is_illegal(record)
        if illegal:
            total += 1
            if record.selected_action == "local" and record.legal_local is False:
                local += 1
            elif record.selected_action == "horizontal" and record.legal_horizontal is False:
                horizontal += 1
            elif record.selected_action == "vertical" and record.legal_vertical is False:
                vertical += 1
            if len(examples) < 5:
                examples.append(
                    {
                        "run_id": record.run_id,
                        "strategy": record.strategy,
                        "seed": record.seed,
                        "decision_opportunity_index": record.decision_opportunity_index,
                        "task_id": record.generated_task_id,
                        "selected_action": record.selected_action,
                        "reason": reason,
                    }
                )
    rate = total / selected_action_count if selected_action_count else None
    return IllegalActionSummary(
        selected_illegal_action_count=total,
        selected_illegal_local_count=local,
        selected_illegal_horizontal_count=horizontal,
        selected_illegal_vertical_count=vertical,
        selected_illegal_action_examples=examples,
        selected_illegal_action_rate=rate,
        evidence_status="available",
    )
