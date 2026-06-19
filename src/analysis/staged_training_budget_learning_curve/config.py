from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

FEATURE_ID = "063-staged-training-budget-learning-curve"
BRANCH_NAME = "063-staged-training-budget-learning-curve"
READY_NEXT_FEATURE = "Feature 064 — Final Review and Release Gate Batch"

OUTPUT_DIR = Path("artifacts/analysis/staged-training-budget-learning-curve")
FIGURES_DIR = OUTPUT_DIR / "figures"
REPORT_JSON = OUTPUT_DIR / "staged-training-budget-learning-curve-report.json"
REPORT_MD = OUTPUT_DIR / "staged-training-budget-learning-curve-report.md"
CHECKPOINT_METRICS_JSON = OUTPUT_DIR / "checkpoint-metrics.json"
COMPARISON_READINESS_JSON = OUTPUT_DIR / "comparison-readiness.json"
STAGED_COMPARATIVE_TABLE_JSON = OUTPUT_DIR / "staged-comparative-table.json"
STAGED_FINDINGS_MD = OUTPUT_DIR / "staged-findings.md"
FIGURE_MANIFEST_JSON = OUTPUT_DIR / "figure-manifest.json"

FEATURE_062_REPORT = Path("artifacts/analysis/unified-campaign-result-analysis-figures-findings/unified-campaign-result-analysis-report.json")
FEATURE_060_BASELINE_EVALUATION_METRICS = Path("artifacts/analysis/full-paper-default-training-campaign-execution/baseline-evaluation-metrics.json")

CHECKPOINT_BUDGETS = (100, 150, 200, 500)
EVALUATION_EPISODES_PER_CHECKPOINT = 100
EPISODE_LENGTH = 110
TRAINING_MODE = "cumulative_staged"
TOTAL_MAX_TRAINING_BUDGET = 500
TRAINING_RERUN_FROM_SCRATCH = False
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
class StagedTrainingBudgetLearningCurveConfig:
    feature_id: str = FEATURE_ID
    feature_062_report_path: Path = FEATURE_062_REPORT
    baseline_reference_metrics_path: Path = FEATURE_060_BASELINE_EVALUATION_METRICS
    output_dir: Path = OUTPUT_DIR
    figures_dir: Path = FIGURES_DIR
    checkpoint_budgets: tuple[int, ...] = CHECKPOINT_BUDGETS
    evaluation_episode_count_per_checkpoint: int = EVALUATION_EPISODES_PER_CHECKPOINT
    episode_length: int = EPISODE_LENGTH
    total_max_training_budget: int = TOTAL_MAX_TRAINING_BUDGET
    training_mode: str = TRAINING_MODE
    training_rerun_from_scratch: bool = TRAINING_RERUN_FROM_SCRATCH
    expected_next_feature: str = READY_NEXT_FEATURE

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 063-staged-training-budget-learning-curve")
        if tuple(self.checkpoint_budgets) != CHECKPOINT_BUDGETS:
            raise ValueError("checkpoint_budgets must equal [100, 150, 200, 500]")
        if self.evaluation_episode_count_per_checkpoint != EVALUATION_EPISODES_PER_CHECKPOINT:
            raise ValueError("evaluation_episode_count_per_checkpoint must equal 100")
        if self.episode_length != EPISODE_LENGTH:
            raise ValueError("episode_length must equal 110")
        if self.total_max_training_budget != TOTAL_MAX_TRAINING_BUDGET:
            raise ValueError("total_max_training_budget must equal 500")
        if self.training_mode != TRAINING_MODE:
            raise ValueError("training_mode must equal cumulative_staged")
        if self.training_rerun_from_scratch is not TRAINING_RERUN_FROM_SCRATCH:
            raise ValueError("training_rerun_from_scratch must remain false")
        if self.expected_next_feature != READY_NEXT_FEATURE:
            raise ValueError("expected_next_feature must route to Feature 064")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "feature_062_report_path": str(self.feature_062_report_path),
            "baseline_reference_metrics_path": str(self.baseline_reference_metrics_path),
            "output_dir": str(self.output_dir),
            "figures_dir": str(self.figures_dir),
            "checkpoint_budgets": list(self.checkpoint_budgets),
            "evaluation_episode_count_per_checkpoint": self.evaluation_episode_count_per_checkpoint,
            "episode_length": self.episode_length,
            "total_max_training_budget": self.total_max_training_budget,
            "training_mode": self.training_mode,
            "training_rerun_from_scratch": self.training_rerun_from_scratch,
            "expected_next_feature": self.expected_next_feature,
        }
