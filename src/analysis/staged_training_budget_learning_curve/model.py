from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .config import CHECKPOINT_BUDGETS, FEATURE_ID, READY_NEXT_FEATURE, SAFETY_FIELDS

ALLOWED_FINAL_VERDICTS = (
    "staged_training_budget_learning_curve_ready",
    "feature_062_prerequisite_blocked",
    "trainer_staging_blocked",
    "checkpoint_evaluation_blocked",
    "metric_schema_blocked",
    "figure_generation_blocked",
    "claim_safety_blocked",
    "scope_drift_detected",
)

REPAIR_ROUTING = {
    "feature_062_prerequisite_blocked": "Repair Feature 062 prerequisite evidence before Feature 063 can proceed",
    "trainer_staging_blocked": "Repair cumulative staged training continuation before Feature 063 can proceed",
    "checkpoint_evaluation_blocked": "Repair checkpoint evaluation evidence before Feature 063 can proceed",
    "metric_schema_blocked": "Repair the checkpoint metric schema before Feature 063 can proceed",
    "figure_generation_blocked": "Repair figure generation before Feature 063 can proceed",
    "claim_safety_blocked": "Repair claim-safety boundaries before Feature 063 can proceed",
    "scope_drift_detected": "Restore approved Feature 063 scope before Feature 063 can proceed",
}


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

    def __post_init__(self) -> None:
        _ensure_int(self.training_budget, "training_budget")
        _ensure_int(self.cumulative_training_episode_count, "cumulative_training_episode_count")
        _ensure_int(self.evaluation_episode_count, "evaluation_episode_count")
        _ensure_int(self.episode_length, "episode_length")
        _ensure_int(self.optimizer_step_count, "optimizer_step_count")
        _ensure_int(self.replay_size, "replay_size")
        _ensure_int(self.action_count_total, "action_count_total")
        _ensure_int(self.loss_count, "loss_count")
        _ensure_bool(self.action_accounting_reconciled, "action_accounting_reconciled")
        _ensure_bool(self.loss_finite, "loss_finite")
        _ensure_bool(self.comparison_ready, "comparison_ready")
        if self.training_budget not in CHECKPOINT_BUDGETS:
            raise ValueError("training_budget must be one of the staged checkpoint budgets")
        if self.episode_length != 110:
            raise ValueError("episode_length must equal 110")
        action_total = sum(int(value) for value in self.action_distribution.values())
        if action_total != self.action_count_total:
            raise ValueError("action_count_total must equal the sum of action_distribution")
        if self.action_count_total != self.replay_size:
            raise ValueError("action_count_total must equal replay_size")
        _required_keys(self.reward_summary, "reward_summary", ("reward_count", "total_reward", "mean_reward"))
        _required_keys(
            self.evaluation_reward_summary,
            "evaluation_reward_summary",
            ("evaluation_episode_count", "mean_reward", "completed_task_count", "dropped_task_count", "terminal_transition_count", "reward_bearing_transition_count"),
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
class ComparisonReadinessSummary:
    comparison_ready: bool
    checkpoint_budgets: list[int]
    ready_checkpoint_budgets: list[int]
    unready_checkpoint_budgets: list[int]
    evaluation_episode_count_per_checkpoint: int
    episode_length: int
    training_mode: str
    baseline_reference_reused: bool
    baseline_reference_artifact_path: str
    baseline_reference_summary: dict[str, Any]
    no_paper_reproduction_claim: bool
    no_performance_superiority_claim: bool
    no_baseline_superiority_claim: bool
    descriptive_only: bool = True

    def __post_init__(self) -> None:
        _ensure_bool(self.comparison_ready, "comparison_ready")
        _ensure_int(self.evaluation_episode_count_per_checkpoint, "evaluation_episode_count_per_checkpoint")
        _ensure_int(self.episode_length, "episode_length")
        _ensure_bool(self.baseline_reference_reused, "baseline_reference_reused")
        _ensure_bool(self.no_paper_reproduction_claim, "no_paper_reproduction_claim")
        _ensure_bool(self.no_performance_superiority_claim, "no_performance_superiority_claim")
        _ensure_bool(self.no_baseline_superiority_claim, "no_baseline_superiority_claim")
        _ensure_bool(self.descriptive_only, "descriptive_only")
        if self.checkpoint_budgets != list(CHECKPOINT_BUDGETS):
            raise ValueError("checkpoint_budgets must equal [100, 150, 200, 500]")
        if self.episode_length != 110:
            raise ValueError("episode_length must equal 110")
        if self.evaluation_episode_count_per_checkpoint != 100:
            raise ValueError("evaluation_episode_count_per_checkpoint must equal 100")

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
        if self.claim_safety_passed:
            if self.paper_reproduction_claim_made or self.performance_superiority_claim_made or self.baseline_superiority_claim_made:
                raise ValueError("claim_safety_passed cannot be true when any unsupported claim is made")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StagedTrainingBudgetLearningCurveReport:
    feature_id: str
    prerequisite_tags_verified: list[dict[str, Any]]
    feature_062_prerequisite_verified: bool
    training_mode: str
    checkpoint_budgets: list[int]
    evaluation_episode_count_per_checkpoint: int
    episode_length: int
    training_rerun_from_scratch: bool
    total_max_training_budget: int
    baseline_reference_summary: dict[str, Any]
    checkpoint_metrics: list[dict[str, Any]]
    comparison_readiness_summary: dict[str, Any]
    staged_comparative_table_summary: dict[str, Any]
    figure_manifest: dict[str, Any]
    claim_safety_status: dict[str, Any]
    remaining_blockers: list[str] = field(default_factory=list)
    recommended_next_feature: str = ""
    final_verdict: str = "feature_062_prerequisite_blocked"

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 063-staged-training-budget-learning-curve")
        if self.final_verdict not in ALLOWED_FINAL_VERDICTS:
            raise ValueError("invalid final_verdict")
        _ensure_unique_names(self.prerequisite_tags_verified, "prerequisite_tags_verified")
        for entry in self.prerequisite_tags_verified:
            _ensure_bool(entry.get("verified"), f"prerequisite_tags_verified.{entry.get('name')}.verified")
        _ensure_bool(self.feature_062_prerequisite_verified, "feature_062_prerequisite_verified")
        _ensure_bool(self.training_rerun_from_scratch, "training_rerun_from_scratch")
        _ensure_int(self.total_max_training_budget, "total_max_training_budget")
        if self.checkpoint_budgets != list(CHECKPOINT_BUDGETS):
            raise ValueError("checkpoint_budgets must equal [100, 150, 200, 500]")
        if self.training_mode != "cumulative_staged":
            raise ValueError("training_mode must equal cumulative_staged")
        if self.evaluation_episode_count_per_checkpoint != 100:
            raise ValueError("evaluation_episode_count_per_checkpoint must equal 100")
        if self.episode_length != 110:
            raise ValueError("episode_length must equal 110")
        if self.total_max_training_budget != 500:
            raise ValueError("total_max_training_budget must equal 500")
        if self.training_rerun_from_scratch is not False:
            raise ValueError("training_rerun_from_scratch must remain false")
        if self.recommended_next_feature != READY_NEXT_FEATURE and self.final_verdict == "staged_training_budget_learning_curve_ready":
            raise ValueError("ready verdict must route to Feature 064")

        checkpoint_metrics = [CheckpointMetric(**metric) for metric in self.checkpoint_metrics]
        if self.final_verdict == "staged_training_budget_learning_curve_ready":
            if self.remaining_blockers:
                raise ValueError("ready verdict cannot include blockers")
            if not self.feature_062_prerequisite_verified:
                raise ValueError("ready verdict requires the Feature 062 prerequisite to be verified")
            if len(checkpoint_metrics) != len(CHECKPOINT_BUDGETS):
                raise ValueError("ready verdict requires four checkpoint metrics")
            if [metric.training_budget for metric in checkpoint_metrics] != list(CHECKPOINT_BUDGETS):
                raise ValueError("ready verdict requires staged checkpoint budgets in order")
            if not self.comparison_readiness_summary.get("comparison_ready"):
                raise ValueError("ready verdict requires comparison readiness")
            if not self.figure_manifest.get("figures_generated"):
                raise ValueError("ready verdict requires generated figures")
            if not self.claim_safety_status.get("claim_safety_passed"):
                raise ValueError("ready verdict requires claim safety")
            if self.recommended_next_feature != READY_NEXT_FEATURE:
                raise ValueError("ready verdict must route to Feature 064")
        if self.claim_safety_status.get("claim_safety_passed") is True:
            if any(
                self.claim_safety_status.get(flag) is True
                for flag in ("paper_reproduction_claim_made", "performance_superiority_claim_made", "baseline_superiority_claim_made")
            ):
                raise ValueError("claim safety passed state cannot contain unsupported claims")
        _required_keys(
            self.comparison_readiness_summary,
            "comparison_readiness_summary",
            (
                "comparison_ready",
                "checkpoint_budgets",
                "ready_checkpoint_budgets",
                "unready_checkpoint_budgets",
                "evaluation_episode_count_per_checkpoint",
                "episode_length",
                "training_mode",
                "baseline_reference_reused",
                "baseline_reference_artifact_path",
                "baseline_reference_summary",
                "no_paper_reproduction_claim",
                "no_performance_superiority_claim",
                "no_baseline_superiority_claim",
            ),
        )
        _required_keys(
            self.figure_manifest,
            "figure_manifest",
            ("figure_directory", "figure_files", "figure_count", "figures_generated"),
        )
        if self.final_verdict == "scope_drift_detected" and not self.remaining_blockers:
            raise ValueError("scope_drift_detected must report blockers")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["checkpoint_metrics"] = [CheckpointMetric(**metric).to_dict() for metric in self.checkpoint_metrics]
        return payload
