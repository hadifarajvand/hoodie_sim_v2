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


def _required_keys(container: dict[str, Any], field_name: str, keys: tuple[str, ...]) -> None:
    missing = [key for key in keys if key not in container]
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
class FeasibilityEstimate:
    local_estimated_execution_slots: int
    horizontal_estimated_transmission_slots: int
    horizontal_estimated_execution_slots: int
    horizontal_estimated_total_slots: int
    vertical_estimated_transmission_slots: int
    vertical_estimated_execution_slots: int
    vertical_estimated_total_slots: int
    deadline_slack_for_local: int
    deadline_slack_for_horizontal: int
    deadline_slack_for_vertical: int
    local_feasible_before_deadline: bool
    horizontal_feasible_before_deadline: bool
    vertical_feasible_before_deadline: bool
    estimate_source: str
    estimate_confidence: str
    missing_fields: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PolicyFeasibilitySummary:
    policy_name: str
    training_budget: int | None
    evaluation_episode_count: int
    episode_length: int
    evaluation_decision_count: int
    action_distribution: dict[str, int]
    canonical_task_count: int
    completed_count: int
    dropped_count: int
    pending_count: int
    completion_ratio: float
    drop_ratio: float
    deadline_violation_ratio: float
    mean_terminal_latency_slots: float | None
    mean_completion_latency_slots: float | None
    mean_drop_latency_slots: float | None
    mean_reward: float
    reward_per_task: float
    reward_per_decision: float
    feasible_task_count_by_action: dict[str, int]
    infeasible_task_count_by_action: dict[str, int]
    completed_feasible_task_count: int
    dropped_feasible_task_count: int
    dropped_infeasible_task_count: int
    runtime_event_audit: dict[str, Any]
    feasibility_summary: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CheckpointFeasibilityMetric:
    training_budget: int
    cumulative_training_episode_count: int
    evaluation_episode_count: int
    episode_length: int
    optimizer_step_count: int
    replay_size: int
    loss_count: int
    last_loss: float | None
    loss_finite: bool
    action_distribution: dict[str, int]
    action_count_total: int
    action_accounting_reconciled: bool
    reward_summary: dict[str, Any]
    completion_path_probe: dict[str, Any]
    full_evaluation_probe: dict[str, Any]
    evaluation_coverage_classification: dict[str, Any]
    task_feasibility_summary: dict[str, Any]
    runtime_event_path_audit: dict[str, Any]
    policy_feasibility_summary: dict[str, Any]
    comparison_ready: bool
    claim_safety_status: dict[str, Any]

    def __post_init__(self) -> None:
        _ensure_int(self.training_budget, "training_budget")
        _ensure_int(self.cumulative_training_episode_count, "cumulative_training_episode_count")
        _ensure_int(self.evaluation_episode_count, "evaluation_episode_count")
        _ensure_int(self.episode_length, "episode_length")
        _ensure_int(self.optimizer_step_count, "optimizer_step_count")
        _ensure_int(self.replay_size, "replay_size")
        _ensure_int(self.loss_count, "loss_count")
        _ensure_bool(self.loss_finite, "loss_finite")
        _ensure_int(self.action_count_total, "action_count_total")
        _ensure_bool(self.action_accounting_reconciled, "action_accounting_reconciled")
        _ensure_bool(self.comparison_ready, "comparison_ready")
        if self.training_budget not in TRAINING_BUDGETS:
            raise ValueError("training_budget must be one of [50, 100]")
        if self.episode_length != 110:
            raise ValueError("episode_length must equal 110")
        if self.evaluation_episode_count != 100:
            raise ValueError("evaluation_episode_count must equal 100")
        _required_keys(self.completion_path_probe, "completion_path_probe", ("sampled_completion_path_probe", "full_evaluation_probe"))
        _required_keys(self.full_evaluation_probe, "full_evaluation_probe", ("evaluation_episode_count", "episode_length", "observed_decision_count"))
        _required_keys(self.evaluation_coverage_classification, "evaluation_coverage_classification", ("evaluation_mode", "one_decision_per_episode_observed", "full_step_decision_coverage_unavailable"))
        _required_keys(self.task_feasibility_summary, "task_feasibility_summary", ("local_feasible_task_count", "horizontal_feasible_task_count", "vertical_feasible_task_count"))
        _required_keys(self.runtime_event_path_audit, "runtime_event_path_audit", ("execution_started_event_count", "execution_progress_event_count", "execution_completed_event_count"))
        _required_keys(self.policy_feasibility_summary, "policy_feasibility_summary", ("policy_results", "candidate_policy_vertical_collapse_in_evaluation"))
        _required_keys(self.claim_safety_status, "claim_safety_status", ("paper_reproduction_claim_made", "performance_superiority_claim_made", "baseline_superiority_claim_made", "claim_safety_passed"))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CompletionPathFeasibilityReport:
    feature_id: str
    base_branch_name: str
    branch_name: str
    checkpoint_budgets: list[int]
    evaluation_episode_count_per_checkpoint: int
    episode_length: int
    expected_max_decision_slots: int
    sampled_completion_path_max_task_decisions: int
    max_training_budget: int
    training_mode: str
    training_rerun_from_scratch: bool
    training_5000_run: bool
    feature_067_prerequisite_verified: bool
    prerequisite_tags_verified: list[dict[str, Any]]
    prerequisite_artifacts: dict[str, Any]
    checkpoint_metrics: list[dict[str, Any]]
    task_feasibility_summary: dict[str, Any]
    action_path_feasibility: dict[str, Any]
    runtime_event_path_audit: dict[str, Any]
    completion_failure_classification: dict[str, Any]
    policy_effect_completion_feasibility: dict[str, Any]
    checkpoint_50_100_feasibility_comparison: dict[str, Any]
    evaluation_coverage_classification: dict[str, Any]
    diagnostic_decision: dict[str, Any]
    claim_safety_status: dict[str, Any]
    figure_manifest: dict[str, Any]
    final_verdict: str
    recommended_next_feature: str
    remaining_blockers: list[str]
    paper_reproduction_claim_made: bool = False
    performance_superiority_claim_made: bool = False
    baseline_superiority_claim_made: bool = False
    environment_files_modified: bool = False
    environment_semantics_modified: bool = False
    environment_modified_files: list[str] = field(default_factory=list)
    environment_modification_reason: str | None = None
    reward_function_modified: bool = False
    policy_modified: bool = False
    dal_modified: bool = False
    dependencies_modified: bool = False
    explanation_of_completion_blocker: str = ""
    scope_guard_summary: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 068-completion-path-deadline-feasibility-repair")
        if self.base_branch_name != "067-terminal-lifecycle-accounting-50-100-comparison":
            raise ValueError("base_branch_name must equal 067-terminal-lifecycle-accounting-50-100-comparison")
        if self.branch_name != FEATURE_ID:
            raise ValueError("branch_name must equal 068-completion-path-deadline-feasibility-repair")
        if tuple(self.checkpoint_budgets) != TRAINING_BUDGETS:
            raise ValueError("checkpoint_budgets must equal [50, 100]")
        if self.evaluation_episode_count_per_checkpoint != 100:
            raise ValueError("evaluation_episode_count_per_checkpoint must equal 100")
        if self.episode_length != 110:
            raise ValueError("episode_length must equal 110")
        if self.expected_max_decision_slots != 11000:
            raise ValueError("expected_max_decision_slots must equal 11000")
        if self.sampled_completion_path_max_task_decisions != 100:
            raise ValueError("sampled_completion_path_max_task_decisions must equal 100")
        if self.max_training_budget != 100:
            raise ValueError("max_training_budget must equal 100")
        if self.training_mode != "cumulative_staged_50_100_completion_feasibility":
            raise ValueError("training_mode must equal cumulative_staged_50_100_completion_feasibility")
        if self.training_rerun_from_scratch is not False:
            raise ValueError("training_rerun_from_scratch must remain false")
        if self.training_5000_run is not False:
            raise ValueError("training_5000_run must remain false")
        if self.final_verdict not in ALLOWED_FINAL_VERDICTS:
            raise ValueError("final_verdict must be one of the allowed verdicts")
        if self.recommended_next_feature != "Deadline / timeout repair":
            raise ValueError("recommended_next_feature must match the feature recommendation")
        if not self.claim_safety_status.get("claim_safety_passed", False):
            raise ValueError("claim_safety_status must pass for a ready report")
        if not isinstance(self.explanation_of_completion_blocker, str):
            raise ValueError("explanation_of_completion_blocker must be a string")
        if not isinstance(self.scope_guard_summary, dict):
            raise ValueError("scope_guard_summary must be a dictionary")
        if self.remaining_blockers and self.final_verdict == "completion_path_feasibility_repair_ready":
            raise ValueError("ready reports cannot carry blockers")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
