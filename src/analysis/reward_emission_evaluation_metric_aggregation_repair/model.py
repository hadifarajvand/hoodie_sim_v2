from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .config import ALLOWED_DIAGNOSTIC_DECISIONS, ALLOWED_FINAL_VERDICTS, CHECKPOINT_BUDGETS, FEATURE_ID


def _ensure_bool(value: Any, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field_name} must be a boolean")
    return value


def _ensure_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int):
        raise ValueError(f"{field_name} must be an integer")
    return value


def _ensure_unique_names(entries: list[dict[str, Any]], field_name: str) -> None:
    names = [str(entry.get("name")) for entry in entries]
    if len(names) != len(set(names)):
        raise ValueError(f"{field_name} names must be unique")


def _required_keys(summary: dict[str, Any], field_name: str, keys: tuple[str, ...]) -> None:
    missing = [key for key in keys if key not in summary]
    if missing:
        raise ValueError(f"{field_name} is missing required keys: {missing}")


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
        if not self.decision_reason.strip():
            raise ValueError("decision_reason must be non-empty")

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
class EvaluationDecisionRecord:
    trace_id: str
    episode_id: int
    task_id: int
    slot: int
    selected_action: str
    legal_action_mask: dict[str, bool]
    source_agent_id: int
    arrival_slot: int
    absolute_deadline_slot: int
    timeout_length: int
    task_size: float
    processing_density: float
    queue_load: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class EvaluationTerminalRecord:
    trace_id: str
    episode_id: int
    task_id: int
    slot: int
    terminal_outcome: str
    selected_action: str | None
    arrival_slot: int
    completion_or_drop_slot: int | None
    latency_slots: int | None
    raw_reward_from_step: float | None
    reward_available_from_step: bool
    finalized_task_index: int
    event_source: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class EvaluationRewardRecord:
    trace_id: str
    episode_id: int
    task_id: int
    slot: int
    selected_action: str | None
    terminal_outcome: str
    raw_reward: float
    reward_event_source: str
    reward_available: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CanonicalTaskOutcome:
    trace_id: str
    episode_id: int
    task_id: int
    selected_action: str | None
    canonical_terminal_outcome: str
    first_decision_slot: int | None
    arrival_slot: int | None
    terminal_slot: int | None
    completion_or_drop_slot: int | None
    latency_slots: int | None
    canonical_reward: float
    raw_reward_total: float
    raw_reward_event_count: int
    raw_terminal_event_count: int
    raw_vs_canonical_reward_delta: float
    duplicate_terminal_event_count: int
    duplicate_reward_event_count: int
    reconciled: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RawVsCanonicalRewardReconciliation:
    raw_event_reward_total: float
    raw_event_reward_count: int
    raw_terminal_event_count: int
    canonical_task_reward_total: float
    canonical_task_reward_count: int
    canonical_task_count: int
    canonical_terminal_task_count: int
    duplicate_terminal_event_count: int
    duplicate_reward_event_count: int
    raw_vs_canonical_reward_delta: float
    reward_reconciled: bool
    raw_reward_event_recovery_blocked: bool
    terminal_event_recovery_blocked: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PaperAlignedDiagnosticMetric:
    training_budget: int
    canonical_completion_ratio: float
    canonical_drop_ratio: float
    canonical_deadline_violation_ratio: float
    canonical_pending_ratio: float
    canonical_mean_completion_latency_slots: float | None
    canonical_mean_drop_latency_slots: float | None
    canonical_mean_terminal_latency_slots: float | None
    canonical_reward_per_task: float
    canonical_reward_per_decision: float
    canonical_tasks_per_decision: float
    reward_reconciliation_status: str
    raw_reward_event_coverage_ratio: float
    terminal_event_coverage_ratio: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CheckpointMetric:
    training_budget: int
    cumulative_training_episode_count: int
    evaluation_episode_count: int
    episode_length: int
    optimizer_step_count: int
    replay_size: int
    action_distribution: dict[str, int]
    action_count_total: int
    action_accounting_reconciled: bool
    loss_count: int
    last_loss: float | None
    loss_finite: bool
    reward_summary: dict[str, Any]
    evaluation_reward_summary: dict[str, Any]
    completed_task_count: int | None = None
    dropped_task_count: int | None = None
    pending_at_horizon_count: int | None = None
    comparison_ready: bool = False
    claim_safety_status: dict[str, Any] = field(default_factory=dict)
    evaluation_action_distribution: dict[str, int] = field(default_factory=dict)
    evaluation_decision_count: int = 0
    evaluation_action_sequence_sample: list[dict[str, Any]] = field(default_factory=list)
    evaluation_legal_action_mask_distribution: dict[str, int] = field(default_factory=dict)
    evaluation_action_by_trace_id: dict[str, Any] = field(default_factory=dict)
    evaluation_action_by_episode_id: dict[str, Any] = field(default_factory=dict)
    replay_window_action_distribution: dict[str, int] = field(default_factory=dict)
    cumulative_training_action_distribution: dict[str, int] = field(default_factory=dict)
    replay_window_is_full_training_history: bool = False
    replay_window_capacity: int = 10_000
    replay_window_interpretation_warning: bool = True
    per_action_outcome_summary: dict[str, Any] = field(default_factory=dict)
    reward_decomposition: dict[str, Any] = field(default_factory=dict)
    event_level_metrics: dict[str, Any] = field(default_factory=dict)
    canonical_task_level_metrics: dict[str, Any] = field(default_factory=dict)
    raw_vs_canonical_metric_comparison: dict[str, Any] = field(default_factory=dict)
    paper_aligned_diagnostic_metrics: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _ensure_int(self.training_budget, "training_budget")
        _ensure_int(self.cumulative_training_episode_count, "cumulative_training_episode_count")
        _ensure_int(self.evaluation_episode_count, "evaluation_episode_count")
        _ensure_int(self.episode_length, "episode_length")
        _ensure_int(self.optimizer_step_count, "optimizer_step_count")
        _ensure_int(self.replay_size, "replay_size")
        _ensure_int(self.action_count_total, "action_count_total")
        _ensure_int(self.loss_count, "loss_count")
        _ensure_int(self.evaluation_decision_count, "evaluation_decision_count")
        _ensure_int(self.replay_window_capacity, "replay_window_capacity")
        _ensure_bool(self.action_accounting_reconciled, "action_accounting_reconciled")
        _ensure_bool(self.loss_finite, "loss_finite")
        _ensure_bool(self.comparison_ready, "comparison_ready")
        _ensure_bool(self.replay_window_is_full_training_history, "replay_window_is_full_training_history")
        _ensure_bool(self.replay_window_interpretation_warning, "replay_window_interpretation_warning")
        if self.training_budget not in CHECKPOINT_BUDGETS:
            raise ValueError("training_budget must be one of the staged checkpoint budgets")
        if self.episode_length != 110:
            raise ValueError("episode_length must equal 110")
        action_total = sum(int(value) for value in self.action_distribution.values())
        if action_total != self.action_count_total:
            raise ValueError("action_count_total must equal the sum of action_distribution")
        if self.action_count_total != self.evaluation_decision_count:
            raise ValueError("evaluation_decision_count must equal action_count_total")
        if self.action_distribution != self.evaluation_action_distribution:
            raise ValueError("evaluation_action_distribution must match action_distribution")
        _required_keys(self.reward_summary, "reward_summary", ("reward_count", "total_reward", "mean_reward"))
        _required_keys(
            self.evaluation_reward_summary,
            "evaluation_reward_summary",
            (
                "evaluation_episode_count",
                "mean_reward",
                "completed_task_count",
                "dropped_task_count",
                "pending_at_horizon_count",
            ),
        )
        _required_keys(
            self.claim_safety_status,
            "claim_safety_status",
            ("claim_safety_passed", "paper_reproduction_claim_made", "performance_superiority_claim_made", "baseline_superiority_claim_made"),
        )
        if self.comparison_ready:
            if self.claim_safety_status.get("claim_safety_passed") is not True:
                raise ValueError("comparison_ready checkpoints must pass claim safety")
            if self.loss_finite is not True:
                raise ValueError("comparison_ready checkpoints must have finite loss")
            if self.action_accounting_reconciled is not True:
                raise ValueError("comparison_ready checkpoints must reconcile action accounting")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RewardEmissionAggregationRepairReport:
    feature_id: str
    base_branch_name: str
    branch_name: str
    prerequisite_tags_verified: list[dict[str, Any]]
    prerequisite_artifacts: dict[str, dict[str, Any]]
    feature_065_prerequisite_verified: bool
    checkpoint_budgets: list[int]
    evaluation_episode_count_per_checkpoint: int
    episode_length: int
    max_training_budget: int
    training_mode: str
    training_rerun_from_scratch: bool
    training_5000_run: bool
    reward_reconciliation_tolerance: float
    checkpoint_metrics: list[dict[str, Any]]
    decision_records_summary: dict[str, Any]
    terminal_event_records: dict[str, Any]
    reward_event_records: dict[str, Any]
    canonical_task_reconciliation: dict[str, Any]
    raw_vs_canonical_reward_reconciliation: dict[str, Any]
    paper_aligned_evaluation_metrics: dict[str, Any]
    policy_effect_after_repair: dict[str, Any]
    diagnostic_decision: dict[str, Any]
    claim_safety_status: dict[str, Any]
    figure_manifest: dict[str, Any]
    remaining_blockers: list[str] = field(default_factory=list)
    final_verdict: str = "reward_emission_aggregation_repair_blocked"
    raw_reward_event_recovery_blocked: bool = False
    terminal_event_recovery_blocked: bool = False
    reward_reconciliation_failed: bool = False
    policy_effect_after_repair_failed: bool = False
    reward_function_modified: bool = False
    environment_semantics_modified: bool = False
    policy_modified: bool = False
    dal_modified: bool = False
    dependencies_modified: bool = False
    paper_reproduction_claim_made: bool = False
    performance_superiority_claim_made: bool = False
    baseline_superiority_claim_made: bool = False
    evaluation_reward_static_after_instrumentation: bool = False
    raw_event_reward_static_across_budget: bool = False
    canonical_task_reward_static_across_budget: bool = False
    canonical_completion_rate_static_across_budget: bool = False
    canonical_drop_rate_static_across_budget: bool = False
    evaluation_action_distribution_static_across_budget: bool = False
    candidate_policy_vertical_collapse_in_evaluation: bool = False
    candidate_policy_vertical_collapse_in_training_replay_window: bool = False
    policy_affects_reward: str = "uncertain"
    policy_affects_terminal_outcomes: str = "uncertain"
    most_likely_root_cause: str = ""
    recommended_next_feature: str = ""
    explanation_of_previous_static_outputs: dict[str, Any] = field(default_factory=dict)
    scope_guard_summary: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 066-reward-emission-evaluation-metric-aggregation-repair")
        if self.base_branch_name != "065-evaluation-instrumentation-reward-state-diagnostic":
            raise ValueError("base_branch_name must equal 065-evaluation-instrumentation-reward-state-diagnostic")
        if self.branch_name != "066-reward-emission-evaluation-metric-aggregation-repair":
            raise ValueError("branch_name must equal 066-reward-emission-evaluation-metric-aggregation-repair")
        if self.checkpoint_budgets != list(CHECKPOINT_BUDGETS):
            raise ValueError("checkpoint_budgets must equal [100, 150, 200, 500]")
        if self.evaluation_episode_count_per_checkpoint != 100:
            raise ValueError("evaluation_episode_count_per_checkpoint must equal 100")
        if self.episode_length != 110:
            raise ValueError("episode_length must equal 110")
        if self.max_training_budget != 500:
            raise ValueError("max_training_budget must equal 500")
        if self.training_mode != "cumulative_staged_diagnostic_repair":
            raise ValueError("training_mode must equal cumulative_staged_diagnostic_repair")
        if self.training_rerun_from_scratch is not False:
            raise ValueError("training_rerun_from_scratch must remain false")
        if self.training_5000_run is not False:
            raise ValueError("training_5000_run must remain false")
        if self.reward_reconciliation_tolerance <= 0:
            raise ValueError("reward_reconciliation_tolerance must be positive")
        if self.final_verdict not in ALLOWED_FINAL_VERDICTS:
            raise ValueError("final_verdict must be one of the allowed verdicts")
        _ensure_unique_names(self.prerequisite_tags_verified, "prerequisite_tags_verified")
        for entry in self.prerequisite_tags_verified:
            _ensure_bool(entry.get("verified"), f"prerequisite_tags_verified.{entry.get('name')}.verified")
        _required_keys(
            self.claim_safety_status,
            "claim_safety_status",
            ("claim_safety_passed", "paper_reproduction_claim_made", "performance_superiority_claim_made", "baseline_superiority_claim_made"),
        )
        if self.final_verdict == "reward_emission_aggregation_repair_ready":
            if self.remaining_blockers:
                raise ValueError("ready verdict cannot include blockers")
            if self.claim_safety_status.get("claim_safety_passed") is not True:
                raise ValueError("ready verdict requires claim safety to pass")
            if not self.recommended_next_feature.strip():
                raise ValueError("ready verdict requires a recommended next feature")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
