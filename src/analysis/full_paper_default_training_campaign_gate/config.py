from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

FEATURE_ID = "059-full-paper-default-training-campaign-gate"
BRANCH_NAME = "059-full-paper-default-training-campaign-gate"
BASE_BRANCH_NAME = "origin/058-evaluation-trace-bank-baseline-harness-hardening"
READY_NEXT_FEATURE = "Feature 060 — Full Paper-Default Training Campaign Execution"

OUTPUT_DIR = Path("artifacts/analysis/full-paper-default-training-campaign-gate")
REPORT_JSON = OUTPUT_DIR / "full-paper-default-training-campaign-gate-report.json"
REPORT_MD = OUTPUT_DIR / "full-paper-default-training-campaign-gate-report.md"

FEATURE_058_REPORT = Path("artifacts/analysis/evaluation-trace-bank-baseline-harness/evaluation-trace-bank-baseline-harness-report.json")
FEATURE_057_REPORT = Path("artifacts/analysis/paper-default-pilot-training-run/paper-default-pilot-training-run-report.json")
FEATURE_056_REPORT = Path("artifacts/analysis/target-update-replay-training-validation/target-update-replay-validation-report.json")
FEATURE_055_REPORT = Path("artifacts/analysis/paper-default-training-smoke-run/paper-default-training-smoke-run-report.json")
FEATURE_058_COMPLETE_TAG = "058-evaluation-trace-bank-baseline-harness-complete"

FULL_CAMPAIGN_OUTPUT_DIR = "artifacts/analysis/full-paper-default-training-campaign-execution/"
CAMPAIGN_RUN_COUNT_OR_EPISODE_BUDGET = {
    "training_episode_count": 1000,
    "evaluation_episode_count": 100,
    "baseline_evaluation_episode_count": 100,
}
RESOURCE_TIMEOUT_BUDGET = {
    "max_wall_clock_minutes": 240,
    "per_episode_timeout_seconds": 120,
}
METRIC_COLLECTION_FIELDS = (
    "delay",
    "drop",
    "timeout",
    "reward",
    "action_distribution",
    "local_action_count",
    "horizontal_action_count",
    "vertical_action_count",
    "per_episode_summary",
    "train_eval_separation",
    "baseline_policy_metrics",
)
EXPECTED_FEATURE_060_ARTIFACTS = {
    "full_campaign_json_report": "artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json",
    "full_campaign_markdown_report": "artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.md",
    "training_metrics_artifact": "artifacts/analysis/full-paper-default-training-campaign-execution/training-metrics.json",
    "evaluation_metrics_artifact": "artifacts/analysis/full-paper-default-training-campaign-execution/evaluation-metrics.json",
    "checkpoint_metadata_artifact": "artifacts/analysis/full-paper-default-training-campaign-execution/checkpoint-metadata.json",
    "run_manifest_artifact": "artifacts/analysis/full-paper-default-training-campaign-execution/run-manifest.json",
}
SAFETY_FIELDS = (
    "no_training_execution",
    "no_optimizer_execution",
    "no_replay_mutation",
    "no_checkpoint_binary_written",
    "no_full_campaign_execution",
    "no_paper_reproduction_claim",
    "no_performance_claim",
    "no_baseline_superiority_claim",
    "no_policy_drift",
    "no_dependency_drift",
    "no_environment_contract_drift",
    "no_reward_timing_change",
    "no_prior_artifact_rewrite",
)


@dataclass(frozen=True, slots=True)
class FullPaperDefaultTrainingCampaignGateConfig:
    feature_id: str = FEATURE_ID
    feature_058_report_path: Path = FEATURE_058_REPORT
    feature_057_report_path: Path = FEATURE_057_REPORT
    feature_056_report_path: Path = FEATURE_056_REPORT
    feature_055_report_path: Path = FEATURE_055_REPORT
    expected_next_feature: str = READY_NEXT_FEATURE
    full_campaign_allowed_next_feature: bool = True
    full_campaign_executed_this_feature: bool = False
    training_executed_this_feature: bool = False
    optimizer_executed_this_feature: bool = False
    replay_mutated_this_feature: bool = False
    checkpoint_binary_written_this_feature: bool = False
    paper_reproduction_claim: bool = False
    performance_claim: bool = False
    baseline_superiority_claim: bool = False

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must remain 059-full-paper-default-training-campaign-gate")
        if self.expected_next_feature != READY_NEXT_FEATURE:
            raise ValueError("Feature 059 pass path must route to Feature 060")
        if self.full_campaign_allowed_next_feature is not True:
            raise ValueError("Feature 059 must allow full campaign only for the next feature")
        forbidden_flags = {
            "full_campaign_executed_this_feature": self.full_campaign_executed_this_feature,
            "training_executed_this_feature": self.training_executed_this_feature,
            "optimizer_executed_this_feature": self.optimizer_executed_this_feature,
            "replay_mutated_this_feature": self.replay_mutated_this_feature,
            "checkpoint_binary_written_this_feature": self.checkpoint_binary_written_this_feature,
            "paper_reproduction_claim": self.paper_reproduction_claim,
            "performance_claim": self.performance_claim,
            "baseline_superiority_claim": self.baseline_superiority_claim,
        }
        enabled = [name for name, value in forbidden_flags.items() if value]
        if enabled:
            raise ValueError(f"Feature 059 forbids enabled behavior flags: {enabled}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "feature_058_report_path": str(self.feature_058_report_path),
            "feature_057_report_path": str(self.feature_057_report_path),
            "feature_056_report_path": str(self.feature_056_report_path),
            "feature_055_report_path": str(self.feature_055_report_path),
            "expected_next_feature": self.expected_next_feature,
            "full_campaign_allowed_next_feature": self.full_campaign_allowed_next_feature,
            "full_campaign_executed_this_feature": self.full_campaign_executed_this_feature,
            "training_executed_this_feature": self.training_executed_this_feature,
            "optimizer_executed_this_feature": self.optimizer_executed_this_feature,
            "replay_mutated_this_feature": self.replay_mutated_this_feature,
            "checkpoint_binary_written_this_feature": self.checkpoint_binary_written_this_feature,
            "paper_reproduction_claim": self.paper_reproduction_claim,
            "performance_claim": self.performance_claim,
            "baseline_superiority_claim": self.baseline_superiority_claim,
        }
