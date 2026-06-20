from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

FEATURE_ID = "068-completion-path-deadline-feasibility-repair"
BASE_BRANCH_NAME = "067-terminal-lifecycle-accounting-50-100-comparison"
BRANCH_NAME = FEATURE_ID

OUTPUT_DIR = Path("artifacts/analysis/completion-path-deadline-feasibility-repair")
FIGURES_DIR = OUTPUT_DIR / "figures"

REPORT_JSON = OUTPUT_DIR / "completion-path-feasibility-report.json"
REPORT_MD = OUTPUT_DIR / "completion-path-feasibility-report.md"
TASK_FEASIBILITY_SUMMARY_JSON = OUTPUT_DIR / "task-feasibility-summary.json"
ACTION_PATH_FEASIBILITY_JSON = OUTPUT_DIR / "action-path-feasibility.json"
RUNTIME_EVENT_PATH_AUDIT_JSON = OUTPUT_DIR / "runtime-event-path-audit.json"
COMPLETION_FAILURE_CLASSIFICATION_JSON = OUTPUT_DIR / "completion-failure-classification.json"
POLICY_EFFECT_COMPLETION_FEASIBILITY_JSON = OUTPUT_DIR / "policy-effect-completion-feasibility.json"
CHECKPOINT_FEASIBILITY_COMPARISON_JSON = OUTPUT_DIR / "checkpoint-50-100-feasibility-comparison.json"
EVALUATION_COVERAGE_CLASSIFICATION_JSON = OUTPUT_DIR / "evaluation-coverage-classification.json"
DIAGNOSTIC_DECISION_JSON = OUTPUT_DIR / "diagnostic-decision.json"
FINAL_COMPLETION_PATH_SUMMARY_MD = OUTPUT_DIR / "final-completion-path-summary.md"
FIGURE_MANIFEST_JSON = OUTPUT_DIR / "figure-manifest.json"

TRAINING_BUDGETS = (50, 100)
MAX_TRAINING_BUDGET = 100
EVALUATION_EPISODE_COUNT_PER_CHECKPOINT = 100
EPISODE_LENGTH = 110
SAMPLED_COMPLETION_PATH_MAX_TASK_DECISIONS = 100
EXPECTED_MAX_DECISION_SLOTS = EVALUATION_EPISODE_COUNT_PER_CHECKPOINT * EPISODE_LENGTH
TRAINING_MODE = "cumulative_staged_50_100_completion_feasibility"
TRAINING_RERUN_FROM_SCRATCH = False
TRAINING_5000_RUN = False
RECORD_SAMPLE_LIMIT = 25
RECOMMENDED_NEXT_FEATURE = "Deadline / timeout repair"
REWARD_RECONCILIATION_TOLERANCE = 1e-9

FEATURE_067_REPORT = Path("artifacts/analysis/terminal-lifecycle-accounting-50-100-comparison/terminal-lifecycle-repair-report.json")

ALLOWED_ROOT_CAUSES = (
    "all_tasks_infeasible_under_current_deadlines",
    "deadline_too_short_for_runtime_model",
    "execution_progress_not_reaching_completion",
    "execution_completion_event_not_emitted",
    "transmission_path_blocks_execution",
    "deadline_sweep_preempts_completion",
    "policy_selects_infeasible_actions",
    "evaluation_probe_too_shallow",
    "unknown_completion_path_failure",
)

ALLOWED_DIAGNOSTIC_DECISIONS = (
    "fix_deadline_timeout_configuration_next",
    "fix_runtime_capacity_or_cycles_model_next",
    "fix_execution_completion_event_emission_next",
    "fix_transmission_to_execution_handoff_next",
    "fix_policy_action_feasibility_filter_next",
    "fix_evaluation_probe_coverage_next",
    "safe_to_proceed_to_state_representation_repair",
    "blocked_due_to_unresolved_completion_path",
)

ALLOWED_FINAL_VERDICTS = (
    "completion_path_feasibility_repair_ready",
    "completion_path_feasibility_repair_blocked",
)


@dataclass(frozen=True, slots=True)
class CompletionPathFeasibilityConfig:
    feature_id: str = FEATURE_ID
    base_branch_name: str = BASE_BRANCH_NAME
    branch_name: str = BRANCH_NAME
    output_dir: Path = OUTPUT_DIR
    figures_dir: Path = FIGURES_DIR
    training_budgets: tuple[int, ...] = TRAINING_BUDGETS
    max_training_budget: int = MAX_TRAINING_BUDGET
    evaluation_episode_count_per_checkpoint: int = EVALUATION_EPISODE_COUNT_PER_CHECKPOINT
    episode_length: int = EPISODE_LENGTH
    sampled_completion_path_max_task_decisions: int = SAMPLED_COMPLETION_PATH_MAX_TASK_DECISIONS
    expected_max_decision_slots: int = EXPECTED_MAX_DECISION_SLOTS
    training_mode: str = TRAINING_MODE
    training_rerun_from_scratch: bool = TRAINING_RERUN_FROM_SCRATCH
    training_5000_run: bool = TRAINING_5000_RUN
    reward_reconciliation_tolerance: float = REWARD_RECONCILIATION_TOLERANCE
    record_sample_limit: int = RECORD_SAMPLE_LIMIT
    recommended_next_feature: str = RECOMMENDED_NEXT_FEATURE

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 068-completion-path-deadline-feasibility-repair")
        if self.base_branch_name != BASE_BRANCH_NAME:
            raise ValueError("base_branch_name must equal 067-terminal-lifecycle-accounting-50-100-comparison")
        if self.branch_name != BRANCH_NAME:
            raise ValueError("branch_name must equal 068-completion-path-deadline-feasibility-repair")
        if tuple(self.training_budgets) != TRAINING_BUDGETS:
            raise ValueError("training_budgets must equal [50, 100]")
        if self.max_training_budget != MAX_TRAINING_BUDGET:
            raise ValueError("max_training_budget must equal 100")
        if self.evaluation_episode_count_per_checkpoint != EVALUATION_EPISODE_COUNT_PER_CHECKPOINT:
            raise ValueError("evaluation_episode_count_per_checkpoint must equal 100")
        if self.episode_length != EPISODE_LENGTH:
            raise ValueError("episode_length must equal 110")
        if self.sampled_completion_path_max_task_decisions != SAMPLED_COMPLETION_PATH_MAX_TASK_DECISIONS:
            raise ValueError("sampled_completion_path_max_task_decisions must equal 100")
        if self.expected_max_decision_slots != EXPECTED_MAX_DECISION_SLOTS:
            raise ValueError("expected_max_decision_slots must equal 11000")
        if self.training_mode != TRAINING_MODE:
            raise ValueError("training_mode must equal cumulative_staged_50_100_completion_feasibility")
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
            "training_budgets": list(self.training_budgets),
            "max_training_budget": self.max_training_budget,
            "evaluation_episode_count_per_checkpoint": self.evaluation_episode_count_per_checkpoint,
            "episode_length": self.episode_length,
            "sampled_completion_path_max_task_decisions": self.sampled_completion_path_max_task_decisions,
            "expected_max_decision_slots": self.expected_max_decision_slots,
            "training_mode": self.training_mode,
            "training_rerun_from_scratch": self.training_rerun_from_scratch,
            "training_5000_run": self.training_5000_run,
            "reward_reconciliation_tolerance": self.reward_reconciliation_tolerance,
            "record_sample_limit": self.record_sample_limit,
            "recommended_next_feature": self.recommended_next_feature,
        }
