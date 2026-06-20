from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .config import ALLOWED_NEXT_ACTIONS, CHECKPOINT_BUDGETS, FEATURE_ID, RECOMMENDED_NEXT_ACTION, SAFETY_FIELDS

ALLOWED_FINAL_VERDICTS = (
    "final_review_release_gate_ready",
    "final_review_release_gate_blocked",
)


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
class RewardStabilityReview:
    evaluation_reward_static_across_budget: bool
    checkpoint_budgets: list[int]
    evaluation_mean_rewards: dict[int, float]
    same_evaluation_trace_bank: bool
    deterministic_evaluation_path: bool
    policy_not_affecting_evaluation_reward: bool
    likely_causes: list[str]
    evidence_notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        _ensure_bool(self.evaluation_reward_static_across_budget, "evaluation_reward_static_across_budget")
        _ensure_bool(self.same_evaluation_trace_bank, "same_evaluation_trace_bank")
        _ensure_bool(self.deterministic_evaluation_path, "deterministic_evaluation_path")
        _ensure_bool(self.policy_not_affecting_evaluation_reward, "policy_not_affecting_evaluation_reward")
        if self.checkpoint_budgets != list(CHECKPOINT_BUDGETS):
            raise ValueError("checkpoint_budgets must equal [100, 150, 200, 500]")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["evaluation_mean_rewards"] = {str(key): value for key, value in self.evaluation_mean_rewards.items()}
        return payload


@dataclass(frozen=True, slots=True)
class ActionCollapseReview:
    vertical_action_collapse_detected: bool
    checkpoint_budgets: list[int]
    action_distributions: dict[int, dict[str, int]]
    vertical_share_by_budget: dict[int, float]
    dominant_action: str
    possible_causes: list[str]
    evidence_notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        _ensure_bool(self.vertical_action_collapse_detected, "vertical_action_collapse_detected")
        if self.checkpoint_budgets != list(CHECKPOINT_BUDGETS):
            raise ValueError("checkpoint_budgets must equal [100, 150, 200, 500]")
        if self.dominant_action != "vertical":
            raise ValueError("dominant_action must be vertical")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["action_distributions"] = {str(key): value for key, value in self.action_distributions.items()}
        payload["vertical_share_by_budget"] = {str(key): value for key, value in self.vertical_share_by_budget.items()}
        return payload


@dataclass(frozen=True, slots=True)
class ReplayBufferReview:
    replay_buffer_capacity: int
    observed_replay_size_by_checkpoint: dict[int, int]
    replay_size_cap_detected: bool
    is_cap_expected: bool
    is_cap_blocking_larger_training: bool
    cap_type: str
    evidence_notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        _ensure_int(self.replay_buffer_capacity, "replay_buffer_capacity")
        _ensure_bool(self.replay_size_cap_detected, "replay_size_cap_detected")
        _ensure_bool(self.is_cap_expected, "is_cap_expected")
        _ensure_bool(self.is_cap_blocking_larger_training, "is_cap_blocking_larger_training")
        if self.replay_buffer_capacity != 10_000:
            raise ValueError("replay_buffer_capacity must equal 10000")
        if self.cap_type not in {"configured_cap", "implementation_cap", "reporting_cap", "unclear"}:
            raise ValueError("invalid cap_type")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["observed_replay_size_by_checkpoint"] = {str(key): value for key, value in self.observed_replay_size_by_checkpoint.items()}
        return payload


@dataclass(frozen=True, slots=True)
class EvaluationSignalReview:
    reward_available: bool
    drop_count_available: bool
    completed_task_count_available: bool
    delay_metric_available: bool
    timeout_metric_available: bool
    train_eval_separation_available: bool
    baseline_metrics_available: bool
    thesis_level_sufficient: bool
    missing_or_null_metrics: list[str]
    comparison_ready: bool
    evidence_notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        _ensure_bool(self.reward_available, "reward_available")
        _ensure_bool(self.drop_count_available, "drop_count_available")
        _ensure_bool(self.completed_task_count_available, "completed_task_count_available")
        _ensure_bool(self.delay_metric_available, "delay_metric_available")
        _ensure_bool(self.timeout_metric_available, "timeout_metric_available")
        _ensure_bool(self.train_eval_separation_available, "train_eval_separation_available")
        _ensure_bool(self.baseline_metrics_available, "baseline_metrics_available")
        _ensure_bool(self.thesis_level_sufficient, "thesis_level_sufficient")
        _ensure_bool(self.comparison_ready, "comparison_ready")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class NextActionDecision:
    recommended_next_action: str
    decision_reason: str
    should_run_larger_training_next: bool
    should_audit_reward_and_evaluation_design_first: bool
    should_fix_action_collapse_first: bool
    should_fix_replay_capacity_or_reporting_first: bool

    def __post_init__(self) -> None:
        if self.recommended_next_action not in ALLOWED_NEXT_ACTIONS:
            raise ValueError("recommended_next_action must be one of the allowed next actions")
        _ensure_bool(self.should_run_larger_training_next, "should_run_larger_training_next")
        _ensure_bool(self.should_audit_reward_and_evaluation_design_first, "should_audit_reward_and_evaluation_design_first")
        _ensure_bool(self.should_fix_action_collapse_first, "should_fix_action_collapse_first")
        _ensure_bool(self.should_fix_replay_capacity_or_reporting_first, "should_fix_replay_capacity_or_reporting_first")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DiagnosticFindings:
    feature_060_prerequisite_verified: bool
    feature_062_prerequisite_verified: bool
    feature_063_prerequisite_verified: bool
    evaluation_reward_static_across_budget: bool
    vertical_action_collapse_detected: bool
    replay_size_cap_detected: bool
    evaluation_signal_sufficient_for_claims: bool
    recommended_next_action: str
    questions: dict[str, dict[str, Any]]

    def __post_init__(self) -> None:
        _ensure_bool(self.feature_060_prerequisite_verified, "feature_060_prerequisite_verified")
        _ensure_bool(self.feature_062_prerequisite_verified, "feature_062_prerequisite_verified")
        _ensure_bool(self.feature_063_prerequisite_verified, "feature_063_prerequisite_verified")
        _ensure_bool(self.evaluation_reward_static_across_budget, "evaluation_reward_static_across_budget")
        _ensure_bool(self.vertical_action_collapse_detected, "vertical_action_collapse_detected")
        _ensure_bool(self.replay_size_cap_detected, "replay_size_cap_detected")
        _ensure_bool(self.evaluation_signal_sufficient_for_claims, "evaluation_signal_sufficient_for_claims")
        if self.recommended_next_action not in ALLOWED_NEXT_ACTIONS:
            raise ValueError("recommended_next_action must be one of the allowed next actions")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class FinalReviewReleaseGateBatchReport:
    feature_id: str
    branch_name: str
    base_branch_name: str
    prerequisite_tags_verified: list[dict[str, Any]]
    prerequisite_artifacts: dict[str, dict[str, Any]]
    feature_060_prerequisite_verified: bool
    feature_062_prerequisite_verified: bool
    feature_063_prerequisite_verified: bool
    feature_063_verified: bool
    checkpoint_budgets: list[int]
    evaluation_episode_count_per_checkpoint: int
    episode_length: int
    training_rerun_from_scratch: bool
    training_5000_run: bool
    artifact_completeness_summary: dict[str, Any]
    claim_boundary_review_summary: dict[str, Any]
    reward_stability_review: dict[str, Any]
    action_collapse_review: dict[str, Any]
    replay_buffer_review: dict[str, Any]
    evaluation_signal_review: dict[str, Any]
    next_action_decision: dict[str, Any]
    diagnostic_findings: dict[str, Any]
    claim_safety_status: dict[str, Any]
    figure_manifest: dict[str, Any]
    scope_guard_summary: dict[str, Any]
    repository_state_audit_summary: dict[str, Any]
    handoff_summary: dict[str, Any]
    safety_summary: dict[str, Any]
    remaining_blockers: list[str] = field(default_factory=list)
    recommended_next_action: str = RECOMMENDED_NEXT_ACTION
    recommended_next_feature: str = "Release tag creation or thesis/paper writing workflow"
    final_verdict: str = "final_review_release_gate_blocked"

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 064-final-review-release-gate-batch")
        if self.final_verdict not in ALLOWED_FINAL_VERDICTS:
            raise ValueError("invalid final_verdict")
        if self.checkpoint_budgets != list(CHECKPOINT_BUDGETS):
            raise ValueError("checkpoint_budgets must equal [100, 150, 200, 500]")
        if self.evaluation_episode_count_per_checkpoint != 100:
            raise ValueError("evaluation_episode_count_per_checkpoint must equal 100")
        if self.episode_length != 110:
            raise ValueError("episode_length must equal 110")
        if self.training_rerun_from_scratch is not False:
            raise ValueError("training_rerun_from_scratch must remain false")
        if self.training_5000_run is not False:
            raise ValueError("training_5000_run must remain false")
        if self.recommended_next_action not in ALLOWED_NEXT_ACTIONS:
            raise ValueError("recommended_next_action must be one of the allowed next actions")
        _ensure_unique_names(self.prerequisite_tags_verified, "prerequisite_tags_verified")
        for entry in self.prerequisite_tags_verified:
            _ensure_bool(entry.get("verified"), f"prerequisite_tags_verified.{entry.get('name')}.verified")

        _required_keys(
            self.artifact_completeness_summary,
            "artifact_completeness_summary",
            ("feature_063_final_exports_exist",),
        )
        _required_keys(
            self.claim_boundary_review_summary,
            "claim_boundary_review_summary",
            ("no_paper_reproduction_claim", "no_performance_superiority_claim", "no_baseline_superiority_claim"),
        )
        _required_keys(
            self.reward_stability_review,
            "reward_stability_review",
            (
                "evaluation_reward_static_across_budget",
                "checkpoint_budgets",
                "evaluation_mean_rewards",
                "same_evaluation_trace_bank",
                "deterministic_evaluation_path",
                "policy_not_affecting_evaluation_reward",
                "likely_causes",
                "evidence_notes",
            ),
        )
        _required_keys(
            self.action_collapse_review,
            "action_collapse_review",
            (
                "vertical_action_collapse_detected",
                "checkpoint_budgets",
                "action_distributions",
                "vertical_share_by_budget",
                "dominant_action",
                "possible_causes",
                "evidence_notes",
            ),
        )
        _required_keys(
            self.replay_buffer_review,
            "replay_buffer_review",
            (
                "replay_buffer_capacity",
                "observed_replay_size_by_checkpoint",
                "replay_size_cap_detected",
                "is_cap_expected",
                "is_cap_blocking_larger_training",
                "cap_type",
                "evidence_notes",
            ),
        )
        _required_keys(
            self.evaluation_signal_review,
            "evaluation_signal_review",
            (
                "reward_available",
                "drop_count_available",
                "completed_task_count_available",
                "delay_metric_available",
                "timeout_metric_available",
                "train_eval_separation_available",
                "baseline_metrics_available",
                "thesis_level_sufficient",
                "missing_or_null_metrics",
                "comparison_ready",
                "evidence_notes",
            ),
        )
        _required_keys(
            self.next_action_decision,
            "next_action_decision",
            (
                "recommended_next_action",
                "decision_reason",
                "should_run_larger_training_next",
                "should_audit_reward_and_evaluation_design_first",
                "should_fix_action_collapse_first",
                "should_fix_replay_capacity_or_reporting_first",
            ),
        )
        _required_keys(
            self.diagnostic_findings,
            "diagnostic_findings",
            (
                "feature_060_prerequisite_verified",
                "feature_062_prerequisite_verified",
                "feature_063_prerequisite_verified",
                "evaluation_reward_static_across_budget",
                "vertical_action_collapse_detected",
                "replay_size_cap_detected",
                "evaluation_signal_sufficient_for_claims",
                "recommended_next_action",
                "questions",
            ),
        )
        _required_keys(
            self.claim_safety_status,
            "claim_safety_status",
            ("paper_reproduction_claim_made", "performance_superiority_claim_made", "baseline_superiority_claim_made", "claim_safety_passed"),
        )
        _required_keys(self.figure_manifest, "figure_manifest", ("figure_directory", "figure_files", "figure_count", "figures_generated"))
        _required_keys(
            self.scope_guard_summary,
            "scope_guard_summary",
            ("working_tree_paths_approved", "staged_paths_approved", "base_branch_head_diff_approved", "forbidden_paths_detected", "approved_paths_detected"),
        )
        _required_keys(self.repository_state_audit_summary, "repository_state_audit_summary", ("release_evidence_mapped_to_source",))
        _required_keys(self.handoff_summary, "handoff_summary", ("next_work_recommendation",))
        _required_keys(self.safety_summary, "safety_summary", ("no_release_tag_created",))
        _required_keys(self.prerequisite_artifacts, "prerequisite_artifacts", tuple(self.prerequisite_artifacts.keys()))

        claim_safety_passed = _ensure_bool(self.claim_safety_status.get("claim_safety_passed"), "claim_safety_status.claim_safety_passed")
        unsupported_claims = any(
            bool(self.claim_safety_status.get(field))
            for field in ("paper_reproduction_claim_made", "performance_superiority_claim_made", "baseline_superiority_claim_made")
        )
        if claim_safety_passed and unsupported_claims:
            raise ValueError("claim safety cannot pass when unsupported claims are made")

        if self.final_verdict == "final_review_release_gate_ready":
            if self.remaining_blockers:
                raise ValueError("ready verdict cannot include blockers")
            if not (
                self.feature_060_prerequisite_verified
                and self.feature_062_prerequisite_verified
                and self.feature_063_prerequisite_verified
            ):
                raise ValueError("ready verdict requires all prerequisites to be verified")
            if self.recommended_next_action != "release_ready_for_thesis_drafting":
                raise ValueError("ready verdict must route to release_ready_for_thesis_drafting")
            if not claim_safety_passed:
                raise ValueError("ready verdict requires claim safety")
            if self.evaluation_signal_review.get("thesis_level_sufficient") is not True:
                raise ValueError("ready verdict requires a sufficient evaluation signal")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
