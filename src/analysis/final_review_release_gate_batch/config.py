from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

FEATURE_ID = "064-final-review-release-gate-batch"
BASE_BRANCH_NAME = "063-staged-training-budget-learning-curve"
BRANCH_NAME = "064-final-review-release-gate-batch"

OUTPUT_DIR = Path("artifacts/analysis/final-review-release-gate-batch")
FIGURES_DIR = OUTPUT_DIR / "figures"
REPORT_JSON = OUTPUT_DIR / "final-review-release-gate-report.json"
REPORT_MD = OUTPUT_DIR / "final-review-release-gate-report.md"
DIAGNOSTIC_FINDINGS_JSON = OUTPUT_DIR / "diagnostic-findings.json"
REWARD_STABILITY_REVIEW_JSON = OUTPUT_DIR / "reward-stability-review.json"
ACTION_COLLAPSE_REVIEW_JSON = OUTPUT_DIR / "action-collapse-review.json"
REPLAY_BUFFER_REVIEW_JSON = OUTPUT_DIR / "replay-buffer-review.json"
EVALUATION_SIGNAL_REVIEW_JSON = OUTPUT_DIR / "evaluation-signal-review.json"
NEXT_ACTION_DECISION_JSON = OUTPUT_DIR / "next-action-decision.json"
FINAL_REVIEW_SUMMARY_MD = OUTPUT_DIR / "final-review-summary.md"
FIGURE_MANIFEST_JSON = OUTPUT_DIR / "figure-manifest.json"

FEATURE_060_REPORT = Path("artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json")
FEATURE_060_TRAINING_METRICS = Path("artifacts/analysis/full-paper-default-training-campaign-execution/training-metrics.json")
FEATURE_060_EVALUATION_METRICS = Path("artifacts/analysis/full-paper-default-training-campaign-execution/evaluation-metrics.json")
FEATURE_060_BASELINE_EVALUATION_METRICS = Path("artifacts/analysis/full-paper-default-training-campaign-execution/baseline-evaluation-metrics.json")

FEATURE_062_REPORT = Path("artifacts/analysis/unified-campaign-result-analysis-figures-findings/unified-campaign-result-analysis-report.json")
FEATURE_062_COMPARISON_READINESS = Path("artifacts/analysis/unified-campaign-result-analysis-figures-findings/comparison-readiness.json")
FEATURE_062_FINAL_FINDINGS = Path("artifacts/analysis/unified-campaign-result-analysis-figures-findings/final-experimental-findings.md")

FEATURE_063_REPORT = Path("artifacts/analysis/staged-training-budget-learning-curve/staged-training-budget-learning-curve-report.json")
FEATURE_063_CHECKPOINT_METRICS = Path("artifacts/analysis/staged-training-budget-learning-curve/checkpoint-metrics.json")
FEATURE_063_COMPARISON_READINESS = Path("artifacts/analysis/staged-training-budget-learning-curve/comparison-readiness.json")
FEATURE_063_STAGED_COMPARATIVE_TABLE = Path("artifacts/analysis/staged-training-budget-learning-curve/staged-comparative-table.json")

CHECKPOINT_BUDGETS = (100, 150, 200, 500)
EVALUATION_EPISODES_PER_CHECKPOINT = 100
EPISODE_LENGTH = 110
TOTAL_MAX_TRAINING_BUDGET = 500
TRAINING_RERUN_FROM_SCRATCH = False
RECOMMENDED_NEXT_ACTION = "audit_reward_and_evaluation_design_before_more_training"

ALLOWED_NEXT_ACTIONS = (
    "release_ready_for_thesis_drafting",
    "run_medium_training_1000_or_2000",
    "run_large_training_5000",
    "audit_reward_and_evaluation_design_before_more_training",
    "fix_action_collapse_before_more_training",
    "fix_replay_capacity_or_reporting_before_more_training",
    "blocked_due_to_artifact_or_metric_inconsistency",
)

SAFETY_FIELDS = (
    "no_paper_reproduction_claim",
    "no_performance_superiority_claim",
    "no_baseline_superiority_claim",
    "no_uncontrolled_campaign_loop",
    "no_policy_drift",
    "no_dependency_drift",
    "no_environment_contract_drift",
    "no_reward_timing_change",
    "no_prior_artifact_rewrite",
)


@dataclass(frozen=True, slots=True)
class FinalReviewReleaseGateBatchConfig:
    feature_id: str = FEATURE_ID
    base_branch_name: str = BASE_BRANCH_NAME
    branch_name: str = BRANCH_NAME
    output_dir: Path = OUTPUT_DIR
    figures_dir: Path = FIGURES_DIR
    checkpoint_budgets: tuple[int, ...] = CHECKPOINT_BUDGETS
    evaluation_episode_count_per_checkpoint: int = EVALUATION_EPISODES_PER_CHECKPOINT
    episode_length: int = EPISODE_LENGTH
    total_max_training_budget: int = TOTAL_MAX_TRAINING_BUDGET
    training_rerun_from_scratch: bool = TRAINING_RERUN_FROM_SCRATCH
    recommended_next_action: str = RECOMMENDED_NEXT_ACTION

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 064-final-review-release-gate-batch")
        if self.base_branch_name != BASE_BRANCH_NAME:
            raise ValueError("base_branch_name must equal 063-staged-training-budget-learning-curve")
        if self.branch_name != BRANCH_NAME:
            raise ValueError("branch_name must equal 064-final-review-release-gate-batch")
        if tuple(self.checkpoint_budgets) != CHECKPOINT_BUDGETS:
            raise ValueError("checkpoint_budgets must equal [100, 150, 200, 500]")
        if self.evaluation_episode_count_per_checkpoint != EVALUATION_EPISODES_PER_CHECKPOINT:
            raise ValueError("evaluation_episode_count_per_checkpoint must equal 100")
        if self.episode_length != EPISODE_LENGTH:
            raise ValueError("episode_length must equal 110")
        if self.total_max_training_budget != TOTAL_MAX_TRAINING_BUDGET:
            raise ValueError("total_max_training_budget must equal 500")
        if self.training_rerun_from_scratch is not TRAINING_RERUN_FROM_SCRATCH:
            raise ValueError("training_rerun_from_scratch must remain false")
        if self.recommended_next_action not in ALLOWED_NEXT_ACTIONS:
            raise ValueError("recommended_next_action must be one of the allowed next actions")

    def required_artifact_paths(self) -> dict[str, Path]:
        return {
            "feature_060_report": FEATURE_060_REPORT,
            "feature_060_training_metrics": FEATURE_060_TRAINING_METRICS,
            "feature_060_evaluation_metrics": FEATURE_060_EVALUATION_METRICS,
            "feature_060_baseline_evaluation_metrics": FEATURE_060_BASELINE_EVALUATION_METRICS,
            "feature_062_report": FEATURE_062_REPORT,
            "feature_062_comparison_readiness": FEATURE_062_COMPARISON_READINESS,
            "feature_062_final_findings": FEATURE_062_FINAL_FINDINGS,
            "feature_063_report": FEATURE_063_REPORT,
            "feature_063_checkpoint_metrics": FEATURE_063_CHECKPOINT_METRICS,
            "feature_063_comparison_readiness": FEATURE_063_COMPARISON_READINESS,
            "feature_063_staged_comparative_table": FEATURE_063_STAGED_COMPARATIVE_TABLE,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "base_branch_name": self.base_branch_name,
            "branch_name": self.branch_name,
            "output_dir": str(self.output_dir),
            "figures_dir": str(self.figures_dir),
            "checkpoint_budgets": list(self.checkpoint_budgets),
            "evaluation_episode_count_per_checkpoint": self.evaluation_episode_count_per_checkpoint,
            "episode_length": self.episode_length,
            "total_max_training_budget": self.total_max_training_budget,
            "training_rerun_from_scratch": self.training_rerun_from_scratch,
            "recommended_next_action": self.recommended_next_action,
            "required_artifact_paths": {name: str(path) for name, path in self.required_artifact_paths().items()},
        }
