from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

FEATURE_ID = "060-full-paper-default-training-campaign-execution"
BRANCH_NAME = "060-full-paper-default-training-campaign-execution-v2"
READY_NEXT_FEATURE = "Feature 061 — Campaign Result Integrity and Comparison Readiness Audit"

OUTPUT_DIR = Path("artifacts/analysis/full-paper-default-training-campaign-execution")
REPORT_JSON = OUTPUT_DIR / "full-paper-default-training-campaign-report.json"
REPORT_MD = OUTPUT_DIR / "full-paper-default-training-campaign-report.md"
TRAINING_METRICS_JSON = OUTPUT_DIR / "training-metrics.json"
EVALUATION_METRICS_JSON = OUTPUT_DIR / "evaluation-metrics.json"
BASELINE_EVALUATION_METRICS_JSON = OUTPUT_DIR / "baseline-evaluation-metrics.json"
CHECKPOINT_METADATA_JSON = OUTPUT_DIR / "checkpoint-metadata.json"
RUN_MANIFEST_JSON = OUTPUT_DIR / "run-manifest.json"

FEATURE_059_REPORT = Path("artifacts/analysis/full-paper-default-training-campaign-gate/full-paper-default-training-campaign-gate-report.json")
FEATURE_058_REPORT = Path("artifacts/analysis/evaluation-trace-bank-baseline-harness/evaluation-trace-bank-baseline-harness-report.json")
FEATURE_057_REPORT = Path("artifacts/analysis/paper-default-pilot-training-run/paper-default-pilot-training-run-report.json")
FEATURE_060A_REPORT = Path("artifacts/analysis/real-trainer-reduced-budget-campaign-execution-validation/real-trainer-reduced-budget-campaign-validation-report.json")
FEATURE_059_COMPLETE_TAG = "059-full-paper-default-training-campaign-gate-complete"

ACTUAL_TRAINING_EPISODE_COUNT = 1000
ACTUAL_EVALUATION_EPISODE_COUNT = 100
ACTUAL_BASELINE_EVALUATION_EPISODE_COUNT = 100
ACTUAL_EPISODE_LENGTH = 110
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
class FullPaperDefaultTrainingCampaignExecutionConfig:
    feature_id: str = FEATURE_ID
    feature_059_report_path: Path = FEATURE_059_REPORT
    feature_058_report_path: Path = FEATURE_058_REPORT
    feature_057_report_path: Path = FEATURE_057_REPORT
    feature_060a_report_path: Path = FEATURE_060A_REPORT
    output_dir: Path = OUTPUT_DIR
    actual_training_episode_count: int = ACTUAL_TRAINING_EPISODE_COUNT
    actual_evaluation_episode_count: int = ACTUAL_EVALUATION_EPISODE_COUNT
    actual_baseline_evaluation_episode_count: int = ACTUAL_BASELINE_EVALUATION_EPISODE_COUNT
    actual_episode_length: int = ACTUAL_EPISODE_LENGTH
    expected_next_feature: str = READY_NEXT_FEATURE
    paper_reproduction_claim: bool = False
    performance_superiority_claim: bool = False
    baseline_superiority_claim: bool = False
    uncontrolled_campaign_loop: bool = False

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must remain 060-full-paper-default-training-campaign-execution")
        if self.expected_next_feature != READY_NEXT_FEATURE:
            raise ValueError("Feature 060 pass path must route to Feature 061")
        if self.actual_training_episode_count <= 0:
            raise ValueError("actual_training_episode_count must be positive")
        if self.actual_evaluation_episode_count <= 0:
            raise ValueError("actual_evaluation_episode_count must be positive")
        if self.actual_baseline_evaluation_episode_count <= 0:
            raise ValueError("actual_baseline_evaluation_episode_count must be positive")
        if self.actual_episode_length != 110:
            raise ValueError("Feature 060 must use paper-default episode length 110")
        forbidden_flags = {
            "paper_reproduction_claim": self.paper_reproduction_claim,
            "performance_superiority_claim": self.performance_superiority_claim,
            "baseline_superiority_claim": self.baseline_superiority_claim,
            "uncontrolled_campaign_loop": self.uncontrolled_campaign_loop,
        }
        enabled = [name for name, value in forbidden_flags.items() if value]
        if enabled:
            raise ValueError(f"Feature 060 forbids enabled behavior flags: {enabled}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "feature_059_report_path": str(self.feature_059_report_path),
            "feature_058_report_path": str(self.feature_058_report_path),
            "feature_057_report_path": str(self.feature_057_report_path),
            "feature_060a_report_path": str(self.feature_060a_report_path),
            "output_dir": str(self.output_dir),
            "actual_training_episode_count": self.actual_training_episode_count,
            "actual_evaluation_episode_count": self.actual_evaluation_episode_count,
            "actual_baseline_evaluation_episode_count": self.actual_baseline_evaluation_episode_count,
            "actual_episode_length": self.actual_episode_length,
            "expected_next_feature": self.expected_next_feature,
            "paper_reproduction_claim": self.paper_reproduction_claim,
            "performance_superiority_claim": self.performance_superiority_claim,
            "baseline_superiority_claim": self.baseline_superiority_claim,
            "uncontrolled_campaign_loop": self.uncontrolled_campaign_loop,
        }
