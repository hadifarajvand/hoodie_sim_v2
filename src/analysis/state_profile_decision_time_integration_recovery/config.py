from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.analysis.full_training_reproduction_campaign.replay import (
    STATE_REPRESENTATION_PROFILE_DEADLINE_QUEUE_FEASIBILITY_V1,
    STATE_REPRESENTATION_PROFILE_LEGACY_MINIMAL,
    state_dimension_for_profile,
)

FEATURE_ID = "072-state-profile-decision-time-integration-recovery"
BASE_BRANCH_NAME = "071-state-representation-deadline-queue-feasibility-repair"
BRANCH_NAME = FEATURE_ID

OUTPUT_DIR = Path("artifacts/analysis/state-profile-decision-time-integration-recovery")
FIGURES_DIR = OUTPUT_DIR / "figures"

STATE_PROFILE_INTEGRATION_REPAIR_REPORT_JSON = OUTPUT_DIR / "state-profile-integration-recovery-report.json"
STATE_PROFILE_INTEGRATION_REPAIR_REPORT_MD = OUTPUT_DIR / "state-profile-integration-recovery-report.md"
DECISION_STATE_INJECTION_AUDIT_JSON = OUTPUT_DIR / "decision-state-injection-audit.json"
TRAIN_EVAL_STATE_PROFILE_CONSISTENCY_JSON = OUTPUT_DIR / "train-eval-state-profile-consistency.json"
REPLAY_STATE_ALIGNMENT_AUDIT_JSON = OUTPUT_DIR / "replay-state-alignment-audit.json"
REAL_RUNNER_VS_ARTIFACT_CONSISTENCY_JSON = OUTPUT_DIR / "real-runner-vs-artifact-consistency.json"
STATE_SAMPLE_RECORDS_AFTER_DECISION_INJECTION_JSON = OUTPUT_DIR / "state-sample-records-after-decision-injection.json"
LEGACY_VS_DECISION_TIME_STATE_COMPARISON_JSON = OUTPUT_DIR / "legacy-vs-decision-time-state-comparison.json"
POLICY_EFFECT_AFTER_DECISION_STATE_FIX_JSON = OUTPUT_DIR / "policy-effect-after-decision-state-fix.json"
RECONCILIATION_AFTER_DECISION_STATE_FIX_JSON = OUTPUT_DIR / "reconciliation-after-decision-state-fix.json"
ACTION_COLLAPSE_AFTER_DECISION_STATE_FIX_JSON = OUTPUT_DIR / "action-collapse-after-decision-state-fix.json"
SELECTED_ACTION_FEASIBILITY_AFTER_DECISION_STATE_FIX_JSON = OUTPUT_DIR / "selected-action-feasibility-after-decision-state-fix.json"
DIAGNOSTIC_DECISION_JSON = OUTPUT_DIR / "diagnostic-decision.json"
FINAL_STATE_PROFILE_INTEGRATION_SUMMARY_MD = OUTPUT_DIR / "final-state-profile-integration-summary.md"
FIGURE_MANIFEST_JSON = OUTPUT_DIR / "figure-manifest.json"
REPORT_JSON = STATE_PROFILE_INTEGRATION_REPAIR_REPORT_JSON
REPORT_MD = STATE_PROFILE_INTEGRATION_REPAIR_REPORT_MD

# Backwards-compatible aliases retained while the 072 code path is being wired.
STATE_REPRESENTATION_REPAIR_REPORT_JSON = STATE_PROFILE_INTEGRATION_REPAIR_REPORT_JSON
STATE_REPRESENTATION_REPAIR_REPORT_MD = STATE_PROFILE_INTEGRATION_REPAIR_REPORT_MD
STATE_FEATURE_COVERAGE_AUDIT_JSON = DECISION_STATE_INJECTION_AUDIT_JSON
STATE_NORMALIZATION_AUDIT_JSON = TRAIN_EVAL_STATE_PROFILE_CONSISTENCY_JSON
LEGACY_VS_NEW_STATE_PROFILE_COMPARISON_JSON = LEGACY_VS_DECISION_TIME_STATE_COMPARISON_JSON
STATE_PROFILE_50_100_COMPARISON_JSON = POLICY_EFFECT_AFTER_DECISION_STATE_FIX_JSON
ACTION_COLLAPSE_DIAGNOSTICS_JSON = ACTION_COLLAPSE_AFTER_DECISION_STATE_FIX_JSON
SELECTED_ACTION_FEASIBILITY_DIAGNOSTICS_JSON = SELECTED_ACTION_FEASIBILITY_AFTER_DECISION_STATE_FIX_JSON
POLICY_EFFECT_AFTER_STATE_REPAIR_JSON = POLICY_EFFECT_AFTER_DECISION_STATE_FIX_JSON
RECONCILIATION_AFTER_STATE_REPAIR_JSON = RECONCILIATION_AFTER_DECISION_STATE_FIX_JSON
FINAL_STATE_REPAIR_SUMMARY_MD = FINAL_STATE_PROFILE_INTEGRATION_SUMMARY_MD

CHECKPOINT_BUDGETS = (50, 100)
TRAINING_BUDGETS = CHECKPOINT_BUDGETS
EVALUATION_EPISODE_COUNT = 100
EPISODE_LENGTH = 110
MAX_TRAINING_BUDGET = 100
TRAINING_MODE = "cumulative_staged_50_100_state_profile_decision_time_integration_recovery"
TRAINING_RERUN_FROM_SCRATCH = False
TRAINING_5000_RUN = False
CALIBRATION_PROFILE_NAME = "paper_aligned_feasible_v1"
LEGACY_STATE_REPRESENTATION_PROFILE = STATE_REPRESENTATION_PROFILE_LEGACY_MINIMAL
NEW_STATE_REPRESENTATION_PROFILE = STATE_REPRESENTATION_PROFILE_DEADLINE_QUEUE_FEASIBILITY_V1

ALLOWED_DIAGNOSTIC_DECISIONS = (
    "safe_to_proceed_to_reward_function_alignment",
    "fix_policy_exploration_next",
    "fix_state_profile_feature_scaling_next",
    "fix_decision_state_injection_next",
    "blocked_due_to_state_profile_integration_failure",
)

ALLOWED_FINAL_VERDICTS = (
    "state_profile_decision_time_integration_ready",
    "state_profile_decision_time_integration_blocked",
)

LEGACY_STATE_DIM = state_dimension_for_profile(LEGACY_STATE_REPRESENTATION_PROFILE)
NEW_STATE_DIM = state_dimension_for_profile(NEW_STATE_REPRESENTATION_PROFILE)


@dataclass(frozen=True, slots=True)
class StateRepresentationRepairConfig:
    feature_id: str = FEATURE_ID
    base_branch_name: str = BASE_BRANCH_NAME
    branch_name: str = BRANCH_NAME
    output_dir: Path = OUTPUT_DIR
    figures_dir: Path = FIGURES_DIR
    checkpoint_budgets: tuple[int, ...] = CHECKPOINT_BUDGETS
    evaluation_episode_count: int = EVALUATION_EPISODE_COUNT
    episode_length: int = EPISODE_LENGTH
    max_training_budget: int = MAX_TRAINING_BUDGET
    training_mode: str = TRAINING_MODE
    training_rerun_from_scratch: bool = TRAINING_RERUN_FROM_SCRATCH
    training_5000_run: bool = TRAINING_5000_RUN
    calibration_profile_name: str = CALIBRATION_PROFILE_NAME
    state_representation_profile: str = NEW_STATE_REPRESENTATION_PROFILE
    legacy_state_representation_profile: str = LEGACY_STATE_REPRESENTATION_PROFILE
    state_dim: int = NEW_STATE_DIM
    legacy_state_dim: int = LEGACY_STATE_DIM
    record_sample_limit: int = 25
    calibration_trace_root_name: str = "calibrated-traces"
    recommended_next_feature: str = "Decision-time state integration"

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 072-state-profile-decision-time-integration-recovery")
        if self.base_branch_name != BASE_BRANCH_NAME:
            raise ValueError("base_branch_name must equal 071-state-representation-deadline-queue-feasibility-repair")
        if self.branch_name != BRANCH_NAME:
            raise ValueError("branch_name must equal 072-state-profile-decision-time-integration-recovery")
        if tuple(self.checkpoint_budgets) != CHECKPOINT_BUDGETS:
            raise ValueError("checkpoint_budgets must equal [50, 100]")
        if self.evaluation_episode_count != EVALUATION_EPISODE_COUNT:
            raise ValueError("evaluation_episode_count must equal 100")
        if self.episode_length != EPISODE_LENGTH:
            raise ValueError("episode_length must equal 110")
        if self.max_training_budget != MAX_TRAINING_BUDGET:
            raise ValueError("max_training_budget must equal 100")
        if self.training_rerun_from_scratch is not False:
            raise ValueError("training_rerun_from_scratch must remain false")
        if self.training_5000_run is not False:
            raise ValueError("training_5000_run must remain false")
        if self.record_sample_limit <= 0:
            raise ValueError("record_sample_limit must be positive")
        if not self.calibration_profile_name.strip():
            raise ValueError("calibration_profile_name must be non-empty")
        if not self.state_representation_profile.strip():
            raise ValueError("state_representation_profile must be non-empty")
        if self.state_dim != NEW_STATE_DIM:
            raise ValueError(f"state_dim must equal {NEW_STATE_DIM} for the new profile")
        if self.legacy_state_dim != LEGACY_STATE_DIM:
            raise ValueError(f"legacy_state_dim must equal {LEGACY_STATE_DIM}")
        if not self.recommended_next_feature.strip():
            raise ValueError("recommended_next_feature must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "base_branch_name": self.base_branch_name,
            "branch_name": self.branch_name,
            "output_dir": str(self.output_dir),
            "figures_dir": str(self.figures_dir),
            "checkpoint_budgets": list(self.checkpoint_budgets),
            "evaluation_episode_count": self.evaluation_episode_count,
            "episode_length": self.episode_length,
            "max_training_budget": self.max_training_budget,
            "training_mode": self.training_mode,
            "training_rerun_from_scratch": self.training_rerun_from_scratch,
            "training_5000_run": self.training_5000_run,
            "calibration_profile_name": self.calibration_profile_name,
            "state_representation_profile": self.state_representation_profile,
            "legacy_state_representation_profile": self.legacy_state_representation_profile,
            "state_dim": self.state_dim,
            "legacy_state_dim": self.legacy_state_dim,
            "record_sample_limit": self.record_sample_limit,
            "calibration_trace_root_name": self.calibration_trace_root_name,
            "recommended_next_feature": self.recommended_next_feature,
        }
