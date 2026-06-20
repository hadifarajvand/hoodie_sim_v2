from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

FEATURE_ID = "070-calibration-metric-consistency-reconciliation-fix"
BASE_BRANCH_NAME = "069-deadline-timeout-feasible-workload-calibration"
BRANCH_NAME = FEATURE_ID

OUTPUT_DIR = Path("artifacts/analysis/calibration-metric-consistency-reconciliation-fix")
FIGURES_DIR = OUTPUT_DIR / "figures"

REPORT_JSON = OUTPUT_DIR / "calibration-metric-consistency-report.json"
REPORT_MD = OUTPUT_DIR / "calibration-metric-consistency-report.md"
METRIC_UNIVERSE_DEFINITIONS_JSON = OUTPUT_DIR / "metric-universe-definitions.json"
POLICY_METRIC_CONSISTENCY_CHECKS_JSON = OUTPUT_DIR / "policy-metric-consistency-checks.json"
REWARD_TERMINAL_RECONCILIATION_FIX_JSON = OUTPUT_DIR / "reward-terminal-reconciliation-fix.json"
ACTION_PATH_DIVERSITY_CHECK_JSON = OUTPUT_DIR / "action-path-diversity-check.json"
CONSISTENT_POLICY_EFFECT_COMPARISON_JSON = OUTPUT_DIR / "consistent-policy-effect-comparison.json"
CONSISTENT_50_100_COMPARISON_JSON = OUTPUT_DIR / "consistent-50-100-comparison.json"
BEFORE_AFTER_CONSISTENCY_COMPARISON_JSON = OUTPUT_DIR / "before-after-consistency-comparison.json"
DIAGNOSTIC_DECISION_JSON = OUTPUT_DIR / "diagnostic-decision.json"
FINAL_CONSISTENCY_SUMMARY_MD = OUTPUT_DIR / "final-consistency-summary.md"
FIGURE_MANIFEST_JSON = OUTPUT_DIR / "figure-manifest.json"

TRAINING_BUDGETS = (50, 100)
MAX_TRAINING_BUDGET = 100
EVALUATION_EPISODE_COUNT = 100
EPISODE_LENGTH = 110
TRAINING_MODE = "cumulative_staged_50_100_calibration_consistency_fix"
TRAINING_RERUN_FROM_SCRATCH = False
TRAINING_5000_RUN = False
RECORD_SAMPLE_LIMIT = 25
REWARD_RECONCILIATION_TOLERANCE = 1e-9
CALIBRATION_PROFILE_NAME = "paper_aligned_feasible_v1"

ALLOWED_FINAL_VERDICTS = (
    "calibration_metric_consistency_reconciliation_ready",
    "calibration_metric_consistency_reconciliation_blocked",
)

ALLOWED_DIAGNOSTIC_DECISIONS = (
    "safe_to_proceed_to_state_representation_repair",
    "safe_to_proceed_to_reward_function_alignment",
    "fix_calibration_action_path_diversity_next",
    "fix_metric_universe_definition_next",
    "fix_reward_terminal_reconciliation_next",
    "blocked_due_to_unresolved_consistency",
)


@dataclass(frozen=True, slots=True)
class CalibrationMetricConsistencyConfig:
    feature_id: str = FEATURE_ID
    base_branch_name: str = BASE_BRANCH_NAME
    branch_name: str = BRANCH_NAME
    output_dir: Path = OUTPUT_DIR
    figures_dir: Path = FIGURES_DIR
    training_budgets: tuple[int, ...] = TRAINING_BUDGETS
    max_training_budget: int = MAX_TRAINING_BUDGET
    evaluation_episode_count: int = EVALUATION_EPISODE_COUNT
    evaluation_episode_count_per_checkpoint: int = EVALUATION_EPISODE_COUNT
    episode_length: int = EPISODE_LENGTH
    training_mode: str = TRAINING_MODE
    training_rerun_from_scratch: bool = TRAINING_RERUN_FROM_SCRATCH
    training_5000_run: bool = TRAINING_5000_RUN
    record_sample_limit: int = RECORD_SAMPLE_LIMIT
    calibration_profile_name: str = CALIBRATION_PROFILE_NAME
    reward_reconciliation_tolerance: float = REWARD_RECONCILIATION_TOLERANCE
    report_source_feature_id: str = "069-deadline-timeout-feasible-workload-calibration"
    prior_report_path: Path = Path("artifacts/analysis/deadline-timeout-feasible-workload-calibration/deadline-timeout-calibration-report.json")

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 070-calibration-metric-consistency-reconciliation-fix")
        if self.base_branch_name != BASE_BRANCH_NAME:
            raise ValueError("base_branch_name must equal 069-deadline-timeout-feasible-workload-calibration")
        if self.branch_name != BRANCH_NAME:
            raise ValueError("branch_name must equal 070-calibration-metric-consistency-reconciliation-fix")
        if tuple(self.training_budgets) != TRAINING_BUDGETS:
            raise ValueError("training_budgets must equal [50, 100]")
        if self.max_training_budget != MAX_TRAINING_BUDGET:
            raise ValueError("max_training_budget must equal 100")
        if self.evaluation_episode_count != EVALUATION_EPISODE_COUNT:
            raise ValueError("evaluation_episode_count must equal 100")
        if self.evaluation_episode_count_per_checkpoint != EVALUATION_EPISODE_COUNT:
            raise ValueError("evaluation_episode_count_per_checkpoint must equal 100")
        if self.episode_length != EPISODE_LENGTH:
            raise ValueError("episode_length must equal 110")
        if self.training_rerun_from_scratch is not False:
            raise ValueError("training_rerun_from_scratch must remain false")
        if self.training_5000_run is not False:
            raise ValueError("training_5000_run must remain false")
        if self.record_sample_limit <= 0:
            raise ValueError("record_sample_limit must be positive")
        if not self.calibration_profile_name.strip():
            raise ValueError("calibration_profile_name must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "base_branch_name": self.base_branch_name,
            "branch_name": self.branch_name,
            "output_dir": str(self.output_dir),
            "figures_dir": str(self.figures_dir),
            "training_budgets": list(self.training_budgets),
            "max_training_budget": self.max_training_budget,
            "evaluation_episode_count": self.evaluation_episode_count,
            "evaluation_episode_count_per_checkpoint": self.evaluation_episode_count_per_checkpoint,
            "episode_length": self.episode_length,
            "training_mode": self.training_mode,
            "training_rerun_from_scratch": self.training_rerun_from_scratch,
            "training_5000_run": self.training_5000_run,
            "record_sample_limit": self.record_sample_limit,
            "calibration_profile_name": self.calibration_profile_name,
            "reward_reconciliation_tolerance": self.reward_reconciliation_tolerance,
            "report_source_feature_id": self.report_source_feature_id,
            "prior_report_path": str(self.prior_report_path),
        }
