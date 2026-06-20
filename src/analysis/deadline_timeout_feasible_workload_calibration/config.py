from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

FEATURE_ID = "069-deadline-timeout-feasible-workload-calibration"
BASE_BRANCH_NAME = "068-completion-path-deadline-feasibility-repair"
BRANCH_NAME = FEATURE_ID

OUTPUT_DIR = Path("artifacts/analysis/deadline-timeout-feasible-workload-calibration")
FIGURES_DIR = OUTPUT_DIR / "figures"

REPORT_JSON = OUTPUT_DIR / "deadline-timeout-calibration-report.json"
REPORT_MD = OUTPUT_DIR / "deadline-timeout-calibration-report.md"
CALIBRATION_CHANGE_LOG_JSON = OUTPUT_DIR / "calibration-change-log.json"
BEFORE_AFTER_FEASIBILITY_COMPARISON_JSON = OUTPUT_DIR / "before-after-feasibility-comparison.json"
CALIBRATED_TASK_FEASIBILITY_SUMMARY_JSON = OUTPUT_DIR / "calibrated-task-feasibility-summary.json"
CALIBRATED_ACTION_PATH_FEASIBILITY_JSON = OUTPUT_DIR / "calibrated-action-path-feasibility.json"
CALIBRATED_POLICY_EFFECT_COMPARISON_JSON = OUTPUT_DIR / "calibrated-policy-effect-comparison.json"
CHECKPOINT_50_100_CALIBRATED_COMPARISON_JSON = OUTPUT_DIR / "checkpoint-50-100-calibrated-comparison.json"
PAPER_ALIGNED_CALIBRATED_METRICS_JSON = OUTPUT_DIR / "paper-aligned-calibrated-metrics.json"
RUNTIME_EVENT_PATH_AFTER_CALIBRATION_JSON = OUTPUT_DIR / "runtime-event-path-after-calibration.json"
DIAGNOSTIC_DECISION_JSON = OUTPUT_DIR / "diagnostic-decision.json"
FINAL_CALIBRATION_SUMMARY_MD = OUTPUT_DIR / "final-calibration-summary.md"
FIGURE_MANIFEST_JSON = OUTPUT_DIR / "figure-manifest.json"

TRAINING_BUDGETS = (50, 100)
MAX_TRAINING_BUDGET = 100
EVALUATION_EPISODE_COUNT = 100
EPISODE_LENGTH = 110
TRAINING_MODE = "cumulative_staged_50_100_feasible_workload_calibration"
TRAINING_RERUN_FROM_SCRATCH = False
TRAINING_5000_RUN = False
RECORD_SAMPLE_LIMIT = 25
CALIBRATION_PROFILE_NAME = "paper_aligned_feasible_v1"
CALIBRATION_TRACE_ROOT_NAME = "calibrated-traces"
RECOMMENDED_NEXT_FEATURE = "State representation repair"

CALIBRATION_NUMBER_OF_AGENTS = 2
CALIBRATION_ARRIVAL_PROBABILITY = 0.15
CALIBRATION_SLOT_DURATION_SECONDS = 0.1
CALIBRATION_TIMEOUT_SLOTS = 15
CALIBRATION_TASK_SIZE_MBITS_MIN = 0.5
CALIBRATION_TASK_SIZE_MBITS_MAX = 60.0
CALIBRATION_TASK_SIZE_MBITS_STEP = 0.5
CALIBRATION_PROCESSING_DENSITY_GCYCLES_PER_MBIT = 0.2
CALIBRATION_CPU_PRIVATE_GCYCLES_PER_SLOT = 0.5
CALIBRATION_CPU_PUBLIC_GCYCLES_PER_SLOT = 0.5
CALIBRATION_CPU_CLOUD_GCYCLES_PER_SLOT = 3.0
CALIBRATION_HORIZONTAL_LINK_RATE_MBPS = 30.0
CALIBRATION_VERTICAL_LINK_RATE_MBPS = 10.0
CALIBRATION_DEADLINE_SLACK_MULTIPLIER = 1.0

ALLOWED_FINAL_VERDICTS = (
    "deadline_timeout_feasible_workload_calibration_ready",
    "deadline_timeout_feasible_workload_calibration_blocked",
)

ALLOWED_DIAGNOSTIC_DECISIONS = (
    "safe_to_proceed_to_state_representation_repair",
    "safe_to_proceed_to_reward_function_alignment",
    "fix_calibration_profile_next",
    "fix_runtime_capacity_or_cycles_model_next",
    "blocked_due_to_unresolved_feasibility",
)


@dataclass(frozen=True, slots=True)
class DeadlineTimeoutCalibrationConfig:
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
    calibration_trace_root_name: str = CALIBRATION_TRACE_ROOT_NAME
    recommended_next_feature: str = RECOMMENDED_NEXT_FEATURE
    number_of_agents: int = CALIBRATION_NUMBER_OF_AGENTS
    arrival_probability: float = CALIBRATION_ARRIVAL_PROBABILITY
    slot_duration_seconds: float = CALIBRATION_SLOT_DURATION_SECONDS
    timeout_slots: int = CALIBRATION_TIMEOUT_SLOTS
    task_size_mbits_min: float = CALIBRATION_TASK_SIZE_MBITS_MIN
    task_size_mbits_max: float = CALIBRATION_TASK_SIZE_MBITS_MAX
    task_size_mbits_step: float = CALIBRATION_TASK_SIZE_MBITS_STEP
    processing_density_gcycles_per_mbit: float = CALIBRATION_PROCESSING_DENSITY_GCYCLES_PER_MBIT
    cpu_capacity_per_slot_private: float = CALIBRATION_CPU_PRIVATE_GCYCLES_PER_SLOT
    cpu_capacity_per_slot_public: float = CALIBRATION_CPU_PUBLIC_GCYCLES_PER_SLOT
    cpu_capacity_per_slot_cloud: float = CALIBRATION_CPU_CLOUD_GCYCLES_PER_SLOT
    horizontal_link_rate_mbps: float = CALIBRATION_HORIZONTAL_LINK_RATE_MBPS
    vertical_link_rate_mbps: float = CALIBRATION_VERTICAL_LINK_RATE_MBPS
    deadline_slack_multiplier: float = CALIBRATION_DEADLINE_SLACK_MULTIPLIER

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 069-deadline-timeout-feasible-workload-calibration")
        if self.base_branch_name != BASE_BRANCH_NAME:
            raise ValueError("base_branch_name must equal 068-completion-path-deadline-feasibility-repair")
        if self.branch_name != BRANCH_NAME:
            raise ValueError("branch_name must equal 069-deadline-timeout-feasible-workload-calibration")
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
            "evaluation_episode_count": self.evaluation_episode_count,
            "evaluation_episode_count_per_checkpoint": self.evaluation_episode_count_per_checkpoint,
            "episode_length": self.episode_length,
            "training_mode": self.training_mode,
            "training_rerun_from_scratch": self.training_rerun_from_scratch,
            "training_5000_run": self.training_5000_run,
            "record_sample_limit": self.record_sample_limit,
            "calibration_profile_name": self.calibration_profile_name,
            "calibration_trace_root_name": self.calibration_trace_root_name,
            "recommended_next_feature": self.recommended_next_feature,
            "number_of_agents": self.number_of_agents,
            "arrival_probability": self.arrival_probability,
            "slot_duration_seconds": self.slot_duration_seconds,
            "timeout_slots": self.timeout_slots,
            "task_size_mbits_min": self.task_size_mbits_min,
            "task_size_mbits_max": self.task_size_mbits_max,
            "task_size_mbits_step": self.task_size_mbits_step,
            "processing_density_gcycles_per_mbit": self.processing_density_gcycles_per_mbit,
            "cpu_capacity_per_slot_private": self.cpu_capacity_per_slot_private,
            "cpu_capacity_per_slot_public": self.cpu_capacity_per_slot_public,
            "cpu_capacity_per_slot_cloud": self.cpu_capacity_per_slot_cloud,
            "horizontal_link_rate_mbps": self.horizontal_link_rate_mbps,
            "vertical_link_rate_mbps": self.vertical_link_rate_mbps,
            "deadline_slack_multiplier": self.deadline_slack_multiplier,
        }
