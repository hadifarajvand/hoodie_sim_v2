from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

FEATURE_ID = "058-evaluation-trace-bank-baseline-harness"
BRANCH_NAME = "058-evaluation-trace-bank-baseline-harness"
READY_NEXT_FEATURE = "Feature 059 — Full Paper-Default Training Campaign Gate"

OUTPUT_DIR = Path("artifacts/analysis/evaluation-trace-bank-baseline-harness")
REPORT_JSON = OUTPUT_DIR / "evaluation-trace-bank-baseline-harness-report.json"
REPORT_MD = OUTPUT_DIR / "evaluation-trace-bank-baseline-harness-report.md"

FEATURE_057_REPORT = Path("artifacts/analysis/paper-default-pilot-training-run/paper-default-pilot-training-run-report.json")
FEATURE_056_REPORT = Path("artifacts/analysis/target-update-replay-training-validation/target-update-replay-validation-report.json")
FEATURE_055_REPORT = Path("artifacts/analysis/paper-default-training-smoke-run/paper-default-training-smoke-run-report.json")
FEATURE_057_COMPLETE_TAG = "057-paper-default-pilot-training-run-complete"

EVALUATION_TRACE_BANK_ID = "feature-058-evaluation-trace-bank"
EVALUATION_TRACE_COUNT = 12
METRIC_SCHEMA_FIELDS = (
    "delay",
    "drop",
    "timeout",
    "reward",
    "action_distribution",
    "local_action_count",
    "horizontal_action_count",
    "vertical_action_count",
    "per_episode_summary",
)
BEHAVIOR_SAFETY_FIELDS = (
    "no_training_execution",
    "no_optimizer_execution",
    "no_replay_mutation",
    "no_checkpoint_binary_written",
    "no_full_campaign",
    "no_paper_reproduction_claim",
    "no_performance_claim",
    "no_policy_drift",
    "no_dependency_drift",
    "no_environment_contract_drift",
    "no_reward_timing_change",
    "no_prior_artifact_rewrite",
)


@dataclass(frozen=True, slots=True)
class EvaluationTraceBankBaselineHarnessConfig:
    feature_id: str = FEATURE_ID
    evaluation_trace_bank_id: str = EVALUATION_TRACE_BANK_ID
    evaluation_trace_count: int = EVALUATION_TRACE_COUNT
    feature_057_report_path: Path = FEATURE_057_REPORT
    feature_056_report_path: Path = FEATURE_056_REPORT
    feature_055_report_path: Path = FEATURE_055_REPORT
    expected_next_feature: str = READY_NEXT_FEATURE
    run_training: bool = False
    run_optimizer: bool = False
    mutate_replay: bool = False
    write_checkpoint_binary: bool = False
    run_full_campaign: bool = False
    claim_paper_reproduction: bool = False
    claim_performance: bool = False

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must remain 058-evaluation-trace-bank-baseline-harness")
        if self.evaluation_trace_count <= 0:
            raise ValueError("evaluation_trace_count must be positive")
        if self.expected_next_feature != READY_NEXT_FEATURE:
            raise ValueError("Feature 058 pass path must route to Feature 059")
        forbidden_flags = {
            "run_training": self.run_training,
            "run_optimizer": self.run_optimizer,
            "mutate_replay": self.mutate_replay,
            "write_checkpoint_binary": self.write_checkpoint_binary,
            "run_full_campaign": self.run_full_campaign,
            "claim_paper_reproduction": self.claim_paper_reproduction,
            "claim_performance": self.claim_performance,
        }
        enabled = [name for name, value in forbidden_flags.items() if value]
        if enabled:
            raise ValueError(f"Feature 058 forbids enabled behavior flags: {enabled}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "evaluation_trace_bank_id": self.evaluation_trace_bank_id,
            "evaluation_trace_count": self.evaluation_trace_count,
            "feature_057_report_path": str(self.feature_057_report_path),
            "feature_056_report_path": str(self.feature_056_report_path),
            "feature_055_report_path": str(self.feature_055_report_path),
            "expected_next_feature": self.expected_next_feature,
            "run_training": self.run_training,
            "run_optimizer": self.run_optimizer,
            "mutate_replay": self.mutate_replay,
            "write_checkpoint_binary": self.write_checkpoint_binary,
            "run_full_campaign": self.run_full_campaign,
            "claim_paper_reproduction": self.claim_paper_reproduction,
            "claim_performance": self.claim_performance,
        }
