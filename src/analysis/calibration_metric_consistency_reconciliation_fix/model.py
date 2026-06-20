from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .config import ALLOWED_DIAGNOSTIC_DECISIONS, ALLOWED_FINAL_VERDICTS, FEATURE_ID, TRAINING_BUDGETS


def _ensure_bool(value: Any, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field_name} must be a boolean")
    return value


def _ensure_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int):
        raise ValueError(f"{field_name} must be an integer")
    return value


def _ensure_nonempty(value: str, field_name: str) -> str:
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
        _ensure_bool(self.paper_reproduction_claim_made, "paper_reproduction_claim_made")
        _ensure_bool(self.performance_superiority_claim_made, "performance_superiority_claim_made")
        _ensure_bool(self.baseline_superiority_claim_made, "baseline_superiority_claim_made")
        _ensure_bool(self.claim_safety_passed, "claim_safety_passed")
        if self.claim_safety_passed and (
            self.paper_reproduction_claim_made or self.performance_superiority_claim_made or self.baseline_superiority_claim_made
        ):
            raise ValueError("claim_safety_passed cannot be true when unsupported claims are made")

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
        _ensure_nonempty(self.decision_reason, "decision_reason")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class FigureManifest:
    figure_directory: str
    figure_files: list[str]
    figure_count: int
    figures_generated: bool

    def __post_init__(self) -> None:
        _ensure_int(self.figure_count, "figure_count")
        _ensure_bool(self.figures_generated, "figures_generated")
        if self.figure_count != len(self.figure_files):
            raise ValueError("figure_count must equal the number of figure_files")
        if self.figures_generated and self.figure_count != 5:
            raise ValueError("figures_generated pass state requires all five figures")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class MetricUniverseDefinitions:
    u_full_decisions: dict[str, Any]
    u_unique_tasks: dict[str, Any]
    u_selected_action_tasks: dict[str, Any]
    u_hypothetical_action_feasibility: dict[str, Any]
    u_reward_events: dict[str, Any]
    u_terminal_events: dict[str, Any]
    feasible_task_count_definition: dict[str, Any]
    completed_feasible_task_count_definition: dict[str, Any]
    reward_event_count_definition: dict[str, Any]
    terminal_event_count_definition: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PolicyMetricConsistency:
    policy_name: str
    checkpoint_budget: int | None
    metric_universes: dict[str, Any]
    decision_count: int
    unique_task_count: int
    terminal_task_count: int
    reward_event_count: int
    selected_action_feasible_task_count: int
    selected_action_infeasible_task_count: int
    hypothetical_local_feasible_task_count: int
    hypothetical_horizontal_feasible_task_count: int
    hypothetical_vertical_feasible_task_count: int
    completed_task_count: int
    dropped_task_count: int
    pending_task_count: int
    completed_selected_action_feasible_count: int
    completed_selected_action_infeasible_count: int
    dropped_selected_action_feasible_count: int
    dropped_selected_action_infeasible_count: int
    feasible_task_count: int
    completed_feasible_task_count: int
    feasible_task_count_universe: str
    completed_feasible_task_count_universe: str
    selected_action_feasible_ratio: float
    hypothetical_local_feasible_ratio: float
    hypothetical_horizontal_feasible_ratio: float
    hypothetical_vertical_feasible_ratio: float
    completion_ratio: float
    drop_ratio: float
    deadline_violation_ratio: float
    mean_reward: float
    reward_per_task: float
    reward_per_decision: float
    mean_completion_latency_slots: float | None
    mean_drop_latency_slots: float | None
    mean_terminal_latency_slots: float | None
    raw_event_reward_total: float
    canonical_task_reward_total: float
    raw_vs_canonical_reward_delta: float
    reward_reconciled: bool
    terminal_reconciled: bool
    reward_reconciliation_status: str
    raw_reward_event_coverage_ratio: float
    terminal_event_coverage_ratio: float
    raw_reward_event_count: int
    raw_terminal_event_count: int
    canonical_task_reward_count: int
    canonical_terminal_task_count: int
    action_distribution: dict[str, int]
    evaluation_action_distribution_source: str
    evaluation_trace_bank_id: str | None
    same_evaluation_trace_bank: bool
    reward_event_recovery_blocked: bool
    terminal_event_recovery_blocked: bool
    completion_path_audit: dict[str, Any]
    paper_aligned_diagnostic_metrics: dict[str, Any]
    task_feasibility_summary: dict[str, Any]
    action_path_feasibility: dict[str, Any]
    sample_task_records: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        _ensure_nonempty(self.policy_name, "policy_name")
        if self.checkpoint_budget is not None and self.checkpoint_budget not in TRAINING_BUDGETS:
            raise ValueError("checkpoint_budget must be one of [50, 100] or None")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ActionPathDiversity:
    checkpoint_budget: int
    count_based_action_feasibility_diversity: bool
    set_based_action_feasibility_diversity: bool
    actions_have_different_feasibility: bool
    feasible_task_count_by_action: dict[str, int]
    feasible_task_set_sizes_by_action: dict[str, int]
    pairwise_set_equality: dict[str, bool]
    pairwise_count_equality: dict[str, bool]
    feasible_task_ids_by_action_sample: dict[str, list[str]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ConsistentPolicyEffectComparison:
    checkpoint_budgets: list[int]
    policy_results: dict[str, Any]
    policy_summaries: dict[str, Any]
    fixed_policy_summaries: dict[str, Any]
    any_fixed_policy_completes: bool
    candidate_policy_at_50: dict[str, Any]
    candidate_policy_at_100: dict[str, Any]
    raw_event_reward_static_across_budget: bool
    canonical_task_reward_static_across_budget: bool
    canonical_completion_rate_static_across_budget: bool
    canonical_drop_rate_static_across_budget: bool
    evaluation_action_distribution_static_across_budget: bool
    policy_affects_reward: str
    policy_affects_terminal_outcomes: str
    candidate_action_distribution_changed_by_budget: bool
    candidate_terminal_outcomes_changed_by_budget: bool
    candidate_policy_vertical_collapse_in_evaluation: bool
    candidate_policy_vertical_collapse_in_training_replay_window: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Consistent50_100Comparison:
    checkpoint_budgets: list[int]
    by_checkpoint: list[dict[str, Any]]
    comparison: dict[str, Any]
    comparison_classification: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class BeforeAfterConsistencyComparison:
    before: dict[str, Any]
    after: dict[str, Any]
    comparison: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CalibrationMetricConsistencyReport:
    feature_id: str
    base_branch_name: str
    branch_name: str
    checkpoint_budgets: list[int]
    evaluation_episode_count: int
    episode_length: int
    max_training_budget: int
    training_mode: str
    training_rerun_from_scratch: bool
    training_5000_run: bool
    calibration_profile_name: str
    metric_universe_definitions: dict[str, Any]
    policy_metric_consistency_checks: dict[str, Any]
    reward_terminal_reconciliation_fix: dict[str, Any]
    action_path_diversity_check: dict[str, Any]
    consistent_policy_effect_comparison: dict[str, Any]
    consistent_50_100_comparison: dict[str, Any]
    before_after_consistency_comparison: dict[str, Any]
    diagnostic_decision: dict[str, Any]
    claim_safety_status: dict[str, Any]
    figure_manifest: dict[str, Any]
    final_verdict: str
    remaining_blockers: list[str]
    recommended_next_feature: str
    feature_069_analysis_code_modified: bool = False
    modified_feature_069_files: list[str] = field(default_factory=list)
    reason: str = ""
    paper_reproduction_claim_made: bool = False
    performance_superiority_claim_made: bool = False
    baseline_superiority_claim_made: bool = False
    reward_function_modified: bool = False
    policy_modified: bool = False
    state_representation_modified: bool = False
    dal_modified: bool = False
    dependencies_modified: bool = False

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 070-calibration-metric-consistency-reconciliation-fix")
        if self.base_branch_name != "069-deadline-timeout-feasible-workload-calibration":
            raise ValueError("base_branch_name must equal 069-deadline-timeout-feasible-workload-calibration")
        if self.branch_name != FEATURE_ID:
            raise ValueError("branch_name must equal 070-calibration-metric-consistency-reconciliation-fix")
        if tuple(self.checkpoint_budgets) != TRAINING_BUDGETS:
            raise ValueError("checkpoint_budgets must equal [50, 100]")
        if self.max_training_budget != 100:
            raise ValueError("max_training_budget must equal 100")
        if self.evaluation_episode_count != 100:
            raise ValueError("evaluation_episode_count must equal 100")
        if self.episode_length != 110:
            raise ValueError("episode_length must equal 110")
        if self.training_rerun_from_scratch is not False:
            raise ValueError("training_rerun_from_scratch must remain false")
        if self.training_5000_run is not False:
            raise ValueError("training_5000_run must remain false")
        if self.final_verdict not in ALLOWED_FINAL_VERDICTS:
            raise ValueError("final_verdict must be one of the allowed final verdicts")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
