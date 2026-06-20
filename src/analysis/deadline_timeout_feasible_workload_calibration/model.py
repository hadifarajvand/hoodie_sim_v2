from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .config import ALLOWED_DIAGNOSTIC_DECISIONS, ALLOWED_FINAL_VERDICTS, FEATURE_ID, TRAINING_BUDGETS


def _require_bool(value: Any, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field_name} must be a boolean")
    return value


def _require_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int):
        raise ValueError(f"{field_name} must be an integer")
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
        _require_int(self.figure_count, "figure_count")
        _require_bool(self.figures_generated, "figures_generated")
        if self.figure_count != len(self.figure_files):
            raise ValueError("figure_count must equal the number of figure_files")
        if self.figures_generated and self.figure_count != 5:
            raise ValueError("figures_generated pass state requires all five figures")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CalibrationChangeLogEntry:
    field_name: str
    before_value: Any
    after_value: Any
    reason: str
    paper_alignment_note: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DeadlineTimeoutCalibrationReport:
    feature_id: str
    base_branch_name: str
    branch_name: str
    calibration_profile_name: str
    checkpoint_budgets: list[int]
    evaluation_episode_count: int
    episode_length: int
    max_training_budget: int
    training_mode: str
    training_rerun_from_scratch: bool
    training_5000_run: bool
    calibration_change_log: list[dict[str, Any]]
    before_overall_feasible_task_ratio: float
    after_overall_feasible_task_ratio: float
    before_completion_count: int
    after_completion_count: int
    before_drop_ratio: float
    after_drop_ratio: float
    before_deadline_violation_ratio: float
    after_deadline_violation_ratio: float
    before_action_path_feasibility: dict[str, Any]
    after_action_path_feasibility: dict[str, Any]
    calibrated_task_feasibility_summary: dict[str, Any]
    calibrated_policy_effect_comparison: dict[str, Any]
    checkpoint_50_100_calibrated_comparison: dict[str, Any]
    paper_aligned_calibrated_metrics: dict[str, Any]
    runtime_event_path_after_calibration: dict[str, Any]
    diagnostic_decision: dict[str, Any]
    claim_safety_status: dict[str, Any]
    figure_manifest: dict[str, Any]
    final_verdict: str
    remaining_blockers: list[str]
    recommended_next_feature: str
    calibration_is_nontrivial: bool
    actions_have_different_feasibility: bool
    deadline_constraints_still_active: bool
    completion_count_nonzero: bool
    drop_count_nonzero: bool
    paper_reproduction_claim_made: bool = False
    performance_superiority_claim_made: bool = False
    baseline_superiority_claim_made: bool = False
    reward_function_modified: bool = False
    policy_modified: bool = False
    state_representation_modified: bool = False
    dal_modified: bool = False
    dependencies_modified: bool = False
    environment_or_generator_files_modified: bool = False
    modified_files: list[str] = field(default_factory=list)
    environment_semantics_modified: bool = False
    calibration_profile_explicit: bool = True
    scope_guard_summary: dict[str, Any] = field(default_factory=dict)
    environment_modification_reason: str | None = None

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 069-deadline-timeout-feasible-workload-calibration")
        if self.base_branch_name != "068-completion-path-deadline-feasibility-repair":
            raise ValueError("base_branch_name must equal 068-completion-path-deadline-feasibility-repair")
        if self.branch_name != FEATURE_ID:
            raise ValueError("branch_name must equal 069-deadline-timeout-feasible-workload-calibration")
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

