from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

FEATURE_ID = "066-reward-emission-evaluation-metric-aggregation-repair"
BASE_BRANCH_NAME = "065-evaluation-instrumentation-reward-state-diagnostic"
BRANCH_NAME = "066-reward-emission-evaluation-metric-aggregation-repair"

OUTPUT_DIR = Path("artifacts/analysis/reward-emission-evaluation-metric-aggregation-repair")
FIGURES_DIR = OUTPUT_DIR / "figures"

REPORT_JSON = OUTPUT_DIR / "reward-emission-aggregation-repair-report.json"
REPORT_MD = OUTPUT_DIR / "reward-emission-aggregation-repair-report.md"
REPAIRED_CHECKPOINT_METRICS_JSON = OUTPUT_DIR / "repaired-instrumented-checkpoint-metrics.json"
REWARD_EVENT_RECORDS_JSON = OUTPUT_DIR / "reward-event-records.json"
TERMINAL_EVENT_RECORDS_JSON = OUTPUT_DIR / "terminal-event-records.json"
DECISION_RECORDS_SUMMARY_JSON = OUTPUT_DIR / "decision-records-summary.json"
CANONICAL_TASK_RECONCILIATION_JSON = OUTPUT_DIR / "canonical-task-reconciliation.json"
RAW_VS_CANONICAL_REWARD_RECONCILIATION_JSON = OUTPUT_DIR / "raw-vs-canonical-reward-reconciliation.json"
PAPER_ALIGNED_EVALUATION_METRICS_JSON = OUTPUT_DIR / "paper-aligned-evaluation-metrics.json"
POLICY_EFFECT_AFTER_REPAIR_JSON = OUTPUT_DIR / "policy-effect-after-repair.json"
DIAGNOSTIC_DECISION_JSON = OUTPUT_DIR / "diagnostic-decision.json"
FINAL_REPAIR_SUMMARY_MD = OUTPUT_DIR / "final-repair-summary.md"
FIGURE_MANIFEST_JSON = OUTPUT_DIR / "figure-manifest.json"

CHECKPOINT_BUDGETS = (100, 150, 200, 500)
EVALUATION_EPISODES_PER_CHECKPOINT = 100
EPISODE_LENGTH = 110
MAX_TRAINING_BUDGET = 500
TRAINING_MODE = "cumulative_staged_diagnostic_repair"
TRAINING_RERUN_FROM_SCRATCH = False
TRAINING_5000_RUN = False
REWARD_RECONCILIATION_TOLERANCE = 1e-9
RECORD_SAMPLE_LIMIT = 25

ALLOWED_DIAGNOSTIC_DECISIONS = (
    "safe_to_proceed_to_state_reward_alignment",
    "fix_environment_lifecycle_accounting_next",
    "fix_reward_function_next",
    "fix_state_representation_next",
    "blocked_due_to_unresolved_reward_event_recovery",
)

ALLOWED_FINAL_VERDICTS = (
    "reward_emission_aggregation_repair_ready",
    "reward_emission_aggregation_repair_blocked",
)

RECOMMENDED_NEXT_FEATURE = "State-reward alignment repair"

FEATURE_065_REPORT = Path("artifacts/analysis/evaluation-instrumentation-reward-state-diagnostic/evaluation-instrumentation-diagnostic-report.json")


@dataclass(frozen=True, slots=True)
class RewardEmissionAggregationRepairConfig:
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
    reward_reconciliation_tolerance: float = REWARD_RECONCILIATION_TOLERANCE
    record_sample_limit: int = RECORD_SAMPLE_LIMIT
    recommended_next_feature: str = RECOMMENDED_NEXT_FEATURE

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 066-reward-emission-evaluation-metric-aggregation-repair")
        if self.base_branch_name != BASE_BRANCH_NAME:
            raise ValueError("base_branch_name must equal 065-evaluation-instrumentation-reward-state-diagnostic")
        if self.branch_name != BRANCH_NAME:
            raise ValueError("branch_name must equal 066-reward-emission-evaluation-metric-aggregation-repair")
        if tuple(self.checkpoint_budgets) != CHECKPOINT_BUDGETS:
            raise ValueError("checkpoint_budgets must equal [100, 150, 200, 500]")
        if self.evaluation_episode_count_per_checkpoint != EVALUATION_EPISODES_PER_CHECKPOINT:
            raise ValueError("evaluation_episode_count_per_checkpoint must equal 100")
        if self.episode_length != EPISODE_LENGTH:
            raise ValueError("episode_length must equal 110")
        if self.max_training_budget != MAX_TRAINING_BUDGET:
            raise ValueError("max_training_budget must equal 500")
        if self.training_mode != TRAINING_MODE:
            raise ValueError("training_mode must equal cumulative_staged_diagnostic_repair")
        if self.training_rerun_from_scratch is not False:
            raise ValueError("training_rerun_from_scratch must remain false")
        if self.training_5000_run is not False:
            raise ValueError("training_5000_run must remain false")
        if self.reward_reconciliation_tolerance <= 0:
            raise ValueError("reward_reconciliation_tolerance must be positive")
        if self.record_sample_limit <= 0:
            raise ValueError("record_sample_limit must be positive")
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
            "reward_reconciliation_tolerance": self.reward_reconciliation_tolerance,
            "record_sample_limit": self.record_sample_limit,
            "recommended_next_feature": self.recommended_next_feature,
        }
