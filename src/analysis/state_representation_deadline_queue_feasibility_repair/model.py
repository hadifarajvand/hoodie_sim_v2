from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .config import ALLOWED_DIAGNOSTIC_DECISIONS, ALLOWED_FINAL_VERDICTS, FEATURE_ID, CHECKPOINT_BUDGETS, LEGACY_STATE_DIM, NEW_STATE_DIM


def _require_bool(value: Any, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field_name} must be a boolean")
    return value


def _require_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int):
        raise ValueError(f"{field_name} must be an integer")
    return value


def _require_nonempty(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


@dataclass(frozen=True, slots=True)
class ClaimSafetyStatus:
    paper_reproduction_claim_made: bool
    performance_superiority_claim_made: bool
    baseline_superiority_claim_made: bool
    claim_safety_passed: bool

    def __post_init__(self) -> None:
        _require_bool(self.paper_reproduction_claim_made, "paper_reproduction_claim_made")
        _require_bool(self.performance_superiority_claim_made, "performance_superiority_claim_made")
        _require_bool(self.baseline_superiority_claim_made, "baseline_superiority_claim_made")
        _require_bool(self.claim_safety_passed, "claim_safety_passed")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DiagnosticDecision:
    recommended_next_action: str
    decision_reason: str
    evidence_notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.recommended_next_action not in ALLOWED_DIAGNOSTIC_DECISIONS:
            raise ValueError("recommended_next_action must be one of the allowed diagnostic decisions")
        _require_nonempty(self.decision_reason, "decision_reason")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class FigureManifest:
    figure_directory: str
    figure_files: list[str]
    figure_count: int
    figures_generated: bool

    def __post_init__(self) -> None:
        _require_int(self.figure_count, "figure_count")
        _require_bool(self.figures_generated, "figures_generated")
        if self.figure_count != len(self.figure_files):
            raise ValueError("figure_count must equal the number of figure_files")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StateFeatureCoverageAudit:
    legacy_state_dim: int
    new_state_dim: int
    added_feature_count: int
    added_feature_names: list[str]
    missing_or_approximated_state_features: list[str]
    state_feature_group_coverage: dict[str, Any]
    state_normalization_summary: dict[str, Any]
    state_sample_records: list[dict[str, Any]]
    train_eval_state_dim_match: bool

    def __post_init__(self) -> None:
        if self.legacy_state_dim != LEGACY_STATE_DIM:
            raise ValueError("legacy_state_dim must equal the legacy profile dimension")
        if self.new_state_dim != NEW_STATE_DIM:
            raise ValueError("new_state_dim must equal the new profile dimension")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StateNormalizationAudit:
    no_nan_in_state_vector: bool
    no_inf_in_state_vector: bool
    state_vector_min: float
    state_vector_max: float
    state_dim_consistent_across_train_eval: bool
    state_samples: list[dict[str, Any]]

    def __post_init__(self) -> None:
        _require_bool(self.no_nan_in_state_vector, "no_nan_in_state_vector")
        _require_bool(self.no_inf_in_state_vector, "no_inf_in_state_vector")
        _require_bool(self.state_dim_consistent_across_train_eval, "state_dim_consistent_across_train_eval")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ActionCollapseDiagnostics:
    legacy_state_dim: int
    new_state_dim: int
    legacy_action_entropy: float
    new_action_entropy: float
    legacy_dominant_action_share: float
    new_dominant_action_share: float
    legacy_is_action_collapsed: bool
    new_is_action_collapsed: bool
    legacy_dominant_action_name: str | None
    new_dominant_action_name: str | None
    action_collapse_reduced: bool

    def __post_init__(self) -> None:
        _require_bool(self.legacy_is_action_collapsed, "legacy_is_action_collapsed")
        _require_bool(self.new_is_action_collapsed, "new_is_action_collapsed")
        _require_bool(self.action_collapse_reduced, "action_collapse_reduced")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SelectedActionFeasibilityDiagnostics:
    legacy_selected_action_feasible_ratio: float
    new_state_selected_action_feasible_ratio: float
    selected_action_feasible_ratio_delta: float
    completed_selected_action_feasible_delta: int
    dropped_selected_action_infeasible_delta: int
    legacy_completed_selected_action_feasible_count: int
    new_completed_selected_action_feasible_count: int
    legacy_dropped_selected_action_feasible_count: int
    new_dropped_selected_action_feasible_count: int
    legacy_selected_action_feasible_task_count: int
    new_state_selected_action_feasible_task_count: int

    def __post_init__(self) -> None:
        _require_int(self.legacy_completed_selected_action_feasible_count, "legacy_completed_selected_action_feasible_count")
        _require_int(self.new_completed_selected_action_feasible_count, "new_completed_selected_action_feasible_count")
        _require_int(self.legacy_dropped_selected_action_feasible_count, "legacy_dropped_selected_action_feasible_count")
        _require_int(self.new_dropped_selected_action_feasible_count, "new_dropped_selected_action_feasible_count")
        _require_int(self.legacy_selected_action_feasible_task_count, "legacy_selected_action_feasible_task_count")
        _require_int(self.new_state_selected_action_feasible_task_count, "new_state_selected_action_feasible_task_count")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PolicyEffectSummary:
    policy_name: str
    checkpoint_budget: int | None
    decision_count: int
    unique_task_count: int
    action_distribution: dict[str, int]
    selected_action_feasible_task_count: int
    selected_action_infeasible_task_count: int
    selected_action_feasible_ratio: float
    completed_count: int
    dropped_count: int
    pending_count: int
    completion_ratio: float
    drop_ratio: float
    deadline_violation_ratio: float
    mean_reward: float
    reward_per_task: float
    reward_per_decision: float
    mean_completion_latency_slots: float | None
    mean_drop_latency_slots: float | None
    mean_terminal_latency_slots: float | None
    reward_reconciled: bool
    terminal_reconciled: bool
    raw_vs_canonical_reward_delta: float
    feasible_task_count: int | None = None
    infeasible_task_count: int | None = None
    action_entropy: float | None = None
    dominant_action_share: float | None = None
    is_action_collapsed: bool | None = None
    dominant_action_name: str | None = None

    def __post_init__(self) -> None:
        _require_nonempty(self.policy_name, "policy_name")
        if self.checkpoint_budget is not None and self.checkpoint_budget not in CHECKPOINT_BUDGETS:
            raise ValueError("checkpoint_budget must be 50, 100, or None")
        _require_bool(self.reward_reconciled, "reward_reconciled")
        _require_bool(self.terminal_reconciled, "terminal_reconciled")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StateProfileComparison:
    legacy_state_dim: int
    new_state_dim: int
    legacy_candidate_50: dict[str, Any]
    legacy_candidate_100: dict[str, Any]
    new_candidate_50: dict[str, Any]
    new_candidate_100: dict[str, Any]
    comparison: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StateRepresentationRepairReport:
    feature_id: str
    base_branch_name: str
    branch_name: str
    feature_070_prerequisite_verified: bool
    metric_universe_consistency_passed: bool
    prerequisite_artifacts: dict[str, Any]
    prerequisite_tags_verified: list[dict[str, Any]]
    scope_guard_summary: dict[str, Any]
    calibration_profile_name: str
    state_representation_profile: str
    legacy_state_representation_profile: str
    checkpoint_budgets: list[int]
    evaluation_episode_count: int
    episode_length: int
    max_training_budget: int
    training_mode: str
    training_rerun_from_scratch: bool
    training_5000_run: bool
    legacy_state_dim: int
    new_state_dim: int
    state_feature_coverage_audit: dict[str, Any]
    state_normalization_audit: dict[str, Any]
    legacy_vs_new_state_profile_comparison: dict[str, Any]
    state_profile_50_100_comparison: dict[str, Any]
    action_collapse_diagnostics: dict[str, Any]
    selected_action_feasibility_diagnostics: dict[str, Any]
    policy_effect_after_state_repair: dict[str, Any]
    reconciliation_after_state_repair: dict[str, Any]
    diagnostic_decision: dict[str, Any]
    claim_safety_status: dict[str, Any]
    figure_manifest: dict[str, Any]
    final_verdict: str
    remaining_blockers: list[str]
    recommended_next_feature: str
    paper_reproduction_claim_made: bool = False
    performance_superiority_claim_made: bool = False
    baseline_superiority_claim_made: bool = False
    reward_function_modified: bool = False
    environment_semantics_modified: bool = False
    policy_algorithm_modified: bool = False
    dal_modified: bool = False
    dependencies_modified: bool = False
    core_state_builder_modified: bool = True
    modified_core_state_files: list[str] = field(default_factory=list)
    modification_reason: str | None = None
    legacy_profile_preserved: bool = True

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 071-state-representation-deadline-queue-feasibility-repair")
        if self.final_verdict not in ALLOWED_FINAL_VERDICTS:
            raise ValueError("final_verdict must be one of the allowed final verdicts")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
