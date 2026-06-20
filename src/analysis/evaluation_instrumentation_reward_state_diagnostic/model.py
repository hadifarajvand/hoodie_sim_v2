from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .config import ALLOWED_DECISIONS, ALLOWED_FINAL_VERDICTS, CHECKPOINT_BUDGETS, FEATURE_ID


def _ensure_bool(value: Any, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field_name} must be a boolean")
    return value


def _ensure_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int):
        raise ValueError(f"{field_name} must be an integer")
    return value


def _required_keys(summary: dict[str, Any], field_name: str, keys: tuple[str, ...]) -> None:
    missing = [key for key in keys if key not in summary]
    if missing:
        raise ValueError(f"{field_name} is missing required keys: {missing}")


def _ensure_unique_names(entries: list[dict[str, Any]], field_name: str) -> None:
    names = [str(entry.get("name")) for entry in entries]
    if len(names) != len(set(names)):
        raise ValueError(f"{field_name} names must be unique")


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
        if self.recommended_next_action not in ALLOWED_DECISIONS:
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
        if self.figures_generated and self.figure_count != 6:
            raise ValueError("figures_generated pass state requires all six figures")

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
                "terminal_transition_count",
                "reward_bearing_transition_count",
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
class EvaluationInstrumentationDiagnosticReport:
    feature_id: str
    base_branch_name: str
    branch_name: str
    prerequisite_tags_verified: list[dict[str, Any]]
    prerequisite_artifacts: dict[str, dict[str, Any]]
    feature_064_prerequisite_verified: bool
    checkpoint_budgets: list[int]
    evaluation_episode_count_per_checkpoint: int
    episode_length: int
    max_training_budget: int
    training_mode: str
    training_rerun_from_scratch: bool
    training_5000_run: bool
    checkpoint_metrics: list[dict[str, Any]]
    evaluation_action_distribution: dict[str, Any]
    per_action_outcome_summary: dict[str, Any]
    reward_decomposition: dict[str, Any]
    replay_window_vs_cumulative_training_actions: dict[str, Any]
    state_feature_coverage_audit: list[dict[str, Any]]
    policy_effect_diagnostic: dict[str, Any]
    diagnostic_decision: dict[str, Any]
    claim_safety_status: dict[str, Any]
    figure_manifest: dict[str, Any]
    diagnostic_findings: dict[str, Any]
    evaluation_action_logging_repair_result: dict[str, Any]
    replay_rolling_window_interpretation_repair_result: dict[str, Any]
    per_action_outcome_attribution_result: dict[str, Any]
    reward_decomposition_result: dict[str, Any]
    state_feature_coverage_audit_result: dict[str, Any]
    policy_effect_diagnostic_result: dict[str, Any]
    explanation_of_previous_static_outputs: dict[str, Any]
    evaluation_reward_static_after_instrumentation: bool
    evaluation_action_distribution_changed_by_budget: bool
    candidate_policy_vertical_collapse_in_evaluation: bool | str
    candidate_policy_vertical_collapse_in_training_replay_window: bool | str
    policy_affects_reward: str
    policy_affects_terminal_outcomes: str
    most_likely_root_cause: str
    recommended_next_feature: str
    remaining_blockers: list[str] = field(default_factory=list)
    final_verdict: str = "evaluation_instrumentation_diagnostic_blocked"

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 065-evaluation-instrumentation-reward-state-diagnostic")
        if self.base_branch_name != "064-final-review-release-gate-batch":
            raise ValueError("base_branch_name must equal 064-final-review-release-gate-batch")
        if self.branch_name != "065-evaluation-instrumentation-reward-state-diagnostic":
            raise ValueError("branch_name must equal 065-evaluation-instrumentation-reward-state-diagnostic")
        if self.checkpoint_budgets != list(CHECKPOINT_BUDGETS):
            raise ValueError("checkpoint_budgets must equal [100, 150, 200, 500]")
        if self.evaluation_episode_count_per_checkpoint != 100:
            raise ValueError("evaluation_episode_count_per_checkpoint must equal 100")
        if self.episode_length != 110:
            raise ValueError("episode_length must equal 110")
        if self.max_training_budget != 500:
            raise ValueError("max_training_budget must equal 500")
        if self.training_mode != "cumulative_staged_diagnostic":
            raise ValueError("training_mode must equal cumulative_staged_diagnostic")
        if self.training_rerun_from_scratch is not False:
            raise ValueError("training_rerun_from_scratch must remain false")
        if self.training_5000_run is not False:
            raise ValueError("training_5000_run must remain false")
        if self.final_verdict not in ALLOWED_FINAL_VERDICTS:
            raise ValueError("final_verdict must be one of the allowed verdicts")
        _ensure_unique_names(self.prerequisite_tags_verified, "prerequisite_tags_verified")
        for entry in self.prerequisite_tags_verified:
            _ensure_bool(entry.get("verified"), f"prerequisite_tags_verified.{entry.get('name')}.verified")
        if self.final_verdict == "evaluation_instrumentation_diagnostic_ready" and self.remaining_blockers:
            raise ValueError("ready verdict cannot include blockers")
        if self.final_verdict == "evaluation_instrumentation_diagnostic_ready" and self.claim_safety_status.get("claim_safety_passed") is not True:
            raise ValueError("ready verdict requires claim safety to pass")
        if self.final_verdict == "evaluation_instrumentation_diagnostic_ready" and not self.recommended_next_feature.strip():
            raise ValueError("ready verdict requires a recommended next feature")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
