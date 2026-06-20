from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

FEATURE_ID = "065-evaluation-instrumentation-reward-state-diagnostic"
BASE_BRANCH_NAME = "064-final-review-release-gate-batch"
BRANCH_NAME = "065-evaluation-instrumentation-reward-state-diagnostic"

OUTPUT_DIR = Path("artifacts/analysis/evaluation-instrumentation-reward-state-diagnostic")
FIGURES_DIR = OUTPUT_DIR / "figures"

REPORT_JSON = OUTPUT_DIR / "evaluation-instrumentation-diagnostic-report.json"
REPORT_MD = OUTPUT_DIR / "evaluation-instrumentation-diagnostic-report.md"
INSTRUMENTED_CHECKPOINT_METRICS_JSON = OUTPUT_DIR / "instrumented-checkpoint-metrics.json"
EVALUATION_ACTION_DISTRIBUTION_JSON = OUTPUT_DIR / "evaluation-action-distribution.json"
PER_ACTION_OUTCOME_SUMMARY_JSON = OUTPUT_DIR / "per-action-outcome-summary.json"
REWARD_DECOMPOSITION_JSON = OUTPUT_DIR / "reward-decomposition.json"
REPLAY_WINDOW_VS_CUMULATIVE_TRAINING_ACTIONS_JSON = OUTPUT_DIR / "replay-window-vs-cumulative-training-actions.json"
STATE_FEATURE_COVERAGE_AUDIT_JSON = OUTPUT_DIR / "state-feature-coverage-audit.json"
POLICY_EFFECT_DIAGNOSTIC_JSON = OUTPUT_DIR / "policy-effect-diagnostic.json"
DIAGNOSTIC_DECISION_JSON = OUTPUT_DIR / "diagnostic-decision.json"
FINAL_DIAGNOSTIC_SUMMARY_MD = OUTPUT_DIR / "final-diagnostic-summary.md"
FIGURE_MANIFEST_JSON = OUTPUT_DIR / "figure-manifest.json"

CHECKPOINT_BUDGETS = (100, 150, 200, 500)
EVALUATION_EPISODES_PER_CHECKPOINT = 100
EPISODE_LENGTH = 110
MAX_TRAINING_BUDGET = 500
TRAINING_MODE = "cumulative_staged_diagnostic"
TRAINING_RERUN_FROM_SCRATCH = False
TRAINING_5000_RUN = False
EVALUATION_ACTION_SEQUENCE_SAMPLE_LIMIT = 25

ALLOWED_DECISIONS = (
    "fix_reward_function_next",
    "fix_state_representation_next",
    "fix_evaluation_metric_aggregation_next",
    "fix_action_collapse_policy_training_next",
    "safe_to_run_medium_training_after_instrumentation",
    "blocked_due_to_unresolved_instrumentation",
)

ALLOWED_FINAL_VERDICTS = (
    "evaluation_instrumentation_diagnostic_ready",
    "evaluation_instrumentation_diagnostic_blocked",
)

RECOMMENDED_NEXT_FEATURE = "Feature 066 — Reward and Evaluation Design Repair"

FEATURE_064_REPORT = Path("artifacts/analysis/final-review-release-gate-batch/final-review-release-gate-report.json")
FEATURE_063_REPORT = Path("artifacts/analysis/staged-training-budget-learning-curve/staged-training-budget-learning-curve-report.json")
FEATURE_063_CHECKPOINT_METRICS = Path("artifacts/analysis/staged-training-budget-learning-curve/checkpoint-metrics.json")
FEATURE_063_COMPARISON_READINESS = Path("artifacts/analysis/staged-training-budget-learning-curve/comparison-readiness.json")
FEATURE_063_STAGED_COMPARATIVE_TABLE = Path("artifacts/analysis/staged-training-budget-learning-curve/staged-comparative-table.json")
FEATURE_062_REPORT = Path("artifacts/analysis/unified-campaign-result-analysis-figures-findings/unified-campaign-result-analysis-report.json")
FEATURE_062_COMPARISON_READINESS = Path("artifacts/analysis/unified-campaign-result-analysis-figures-findings/comparison-readiness.json")
FEATURE_062_FINAL_FINDINGS = Path("artifacts/analysis/unified-campaign-result-analysis-figures-findings/final-experimental-findings.md")
FEATURE_060_REPORT = Path("artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json")
FEATURE_060_TRAINING_METRICS = Path("artifacts/analysis/full-paper-default-training-campaign-execution/training-metrics.json")
FEATURE_060_EVALUATION_METRICS = Path("artifacts/analysis/full-paper-default-training-campaign-execution/evaluation-metrics.json")
FEATURE_060_BASELINE_EVALUATION_METRICS = Path("artifacts/analysis/full-paper-default-training-campaign-execution/baseline-evaluation-metrics.json")

SAFETY_FIELDS = (
    "no_paper_reproduction_claim",
    "no_performance_superiority_claim",
    "no_baseline_superiority_claim",
    "no_reward_semantics_change",
    "no_environment_semantics_change",
    "no_policy_semantics_change",
    "no_dal_semantics_change",
    "no_replay_semantics_change",
)


@dataclass(frozen=True, slots=True)
class EvaluationInstrumentationDiagnosticConfig:
    feature_id: str = FEATURE_ID
    base_branch_name: str = BASE_BRANCH_NAME
    branch_name: str = BRANCH_NAME
    output_dir: Path = OUTPUT_DIR
    figures_dir: Path = FIGURES_DIR
    checkpoint_budgets: tuple[int, ...] = CHECKPOINT_BUDGETS
    evaluation_episode_count_per_checkpoint: int = EVALUATION_EPISODES_PER_CHECKPOINT
    episode_length: int = EPISODE_LENGTH
    max_training_budget: int = MAX_TRAINING_BUDGET
    training_mode: str = TRAINING_MODE
    training_rerun_from_scratch: bool = TRAINING_RERUN_FROM_SCRATCH
    training_5000_run: bool = TRAINING_5000_RUN
    evaluation_action_sequence_sample_limit: int = EVALUATION_ACTION_SEQUENCE_SAMPLE_LIMIT
    recommended_next_feature: str = RECOMMENDED_NEXT_FEATURE

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 065-evaluation-instrumentation-reward-state-diagnostic")
        if self.base_branch_name != BASE_BRANCH_NAME:
            raise ValueError("base_branch_name must equal 064-final-review-release-gate-batch")
        if self.branch_name != BRANCH_NAME:
            raise ValueError("branch_name must equal 065-evaluation-instrumentation-reward-state-diagnostic")
        if tuple(self.checkpoint_budgets) != CHECKPOINT_BUDGETS:
            raise ValueError("checkpoint_budgets must equal [100, 150, 200, 500]")
        if self.evaluation_episode_count_per_checkpoint != EVALUATION_EPISODES_PER_CHECKPOINT:
            raise ValueError("evaluation_episode_count_per_checkpoint must equal 100")
        if self.episode_length != EPISODE_LENGTH:
            raise ValueError("episode_length must equal 110")
        if self.max_training_budget != MAX_TRAINING_BUDGET:
            raise ValueError("max_training_budget must equal 500")
        if self.training_mode != TRAINING_MODE:
            raise ValueError("training_mode must equal cumulative_staged_diagnostic")
        if self.training_rerun_from_scratch is not TRAINING_RERUN_FROM_SCRATCH:
            raise ValueError("training_rerun_from_scratch must remain false")
        if self.training_5000_run is not TRAINING_5000_RUN:
            raise ValueError("training_5000_run must remain false")
        if self.evaluation_action_sequence_sample_limit <= 0:
            raise ValueError("evaluation_action_sequence_sample_limit must be positive")
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
            "evaluation_episode_count_per_checkpoint": self.evaluation_episode_count_per_checkpoint,
            "episode_length": self.episode_length,
            "max_training_budget": self.max_training_budget,
            "training_mode": self.training_mode,
            "training_rerun_from_scratch": self.training_rerun_from_scratch,
            "training_5000_run": self.training_5000_run,
            "evaluation_action_sequence_sample_limit": self.evaluation_action_sequence_sample_limit,
            "recommended_next_feature": self.recommended_next_feature,
        }
