from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

FEATURE_ID = "060a-real-trainer-reduced-budget-campaign-execution-validation"
BRANCH_NAME = "060a-real-trainer-reduced-budget-campaign-execution-validation"
READY_NEXT_FEATURE = "Feature 060 — Full Paper-Default Training Campaign Execution"

OUTPUT_DIR = Path("artifacts/analysis/real-trainer-reduced-budget-campaign-execution-validation")
REPORT_JSON = OUTPUT_DIR / "real-trainer-reduced-budget-campaign-validation-report.json"
REPORT_MD = OUTPUT_DIR / "real-trainer-reduced-budget-campaign-validation-report.md"
TRAINING_METRICS_JSON = OUTPUT_DIR / "training-metrics.json"
EVALUATION_METRICS_JSON = OUTPUT_DIR / "evaluation-metrics.json"
CHECKPOINT_METADATA_JSON = OUTPUT_DIR / "checkpoint-metadata.json"
RUN_MANIFEST_JSON = OUTPUT_DIR / "run-manifest.json"

FEATURE_059_REPORT = Path("artifacts/analysis/full-paper-default-training-campaign-gate/full-paper-default-training-campaign-gate-report.json")
FEATURE_058_REPORT = Path("artifacts/analysis/evaluation-trace-bank-baseline-harness/evaluation-trace-bank-baseline-harness-report.json")
FEATURE_057_REPORT = Path("artifacts/analysis/paper-default-pilot-training-run/paper-default-pilot-training-run-report.json")


@dataclass(frozen=True, slots=True)
class RealTrainerReducedBudgetCampaignExecutionValidationConfig:
    feature_id: str = FEATURE_ID
    feature_059_report_path: Path = FEATURE_059_REPORT
    feature_058_report_path: Path = FEATURE_058_REPORT
    feature_057_report_path: Path = FEATURE_057_REPORT
    output_dir: Path = OUTPUT_DIR
    actual_training_episode_count: int = 1
    actual_episode_length: int = 110
    actual_baseline_evaluation_episode_count: int = 1
    actual_evaluation_episode_count: int = 3
    expected_next_feature: str = READY_NEXT_FEATURE
    full_campaign_executed: bool = False
    paper_reproduction_claim: bool = False
    performance_superiority_claim: bool = False
    baseline_superiority_claim: bool = False

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must remain 060a-real-trainer-reduced-budget-campaign-execution-validation")
        if self.actual_training_episode_count <= 0:
            raise ValueError("actual_training_episode_count must be positive")
        if self.actual_episode_length != 110:
            raise ValueError("Feature 060A must use paper-default episode length 110")
        if self.actual_baseline_evaluation_episode_count <= 0:
            raise ValueError("actual_baseline_evaluation_episode_count must be positive")
        if self.actual_evaluation_episode_count <= 0:
            raise ValueError("actual_evaluation_episode_count must be positive")
        if self.expected_next_feature != READY_NEXT_FEATURE:
            raise ValueError("Feature 060A must route the pass path to Feature 060")
        for field_name in ("full_campaign_executed", "paper_reproduction_claim", "performance_superiority_claim", "baseline_superiority_claim"):
            if getattr(self, field_name) is not False:
                raise ValueError(f"{field_name} must remain false")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "feature_059_report_path": str(self.feature_059_report_path),
            "feature_058_report_path": str(self.feature_058_report_path),
            "feature_057_report_path": str(self.feature_057_report_path),
            "output_dir": str(self.output_dir),
            "actual_training_episode_count": self.actual_training_episode_count,
            "actual_episode_length": self.actual_episode_length,
            "actual_baseline_evaluation_episode_count": self.actual_baseline_evaluation_episode_count,
            "actual_evaluation_episode_count": self.actual_evaluation_episode_count,
            "expected_next_feature": self.expected_next_feature,
            "full_campaign_executed": self.full_campaign_executed,
            "paper_reproduction_claim": self.paper_reproduction_claim,
            "performance_superiority_claim": self.performance_superiority_claim,
            "baseline_superiority_claim": self.baseline_superiority_claim,
        }
