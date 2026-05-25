from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

FEATURE_ID = "061-campaign-integrity-evaluation-comparison-batch"
BRANCH_NAME = "061-campaign-integrity-evaluation-comparison-batch"
BASE_BRANCH = "main"
READY_NEXT_FEATURE = "Feature 062 — Multi-Seed Campaign and Ablation Batch"

OUTPUT_DIR = Path("artifacts/analysis/campaign-integrity-evaluation-comparison-batch")
REPORT_JSON = OUTPUT_DIR / "campaign-integrity-evaluation-comparison-batch-report.json"
REPORT_MD = OUTPUT_DIR / "campaign-integrity-evaluation-comparison-batch-report.md"
BASELINE_RESULTS_JSON = OUTPUT_DIR / "baseline-evaluation-results.json"
TRAINED_POLICY_RESULTS_JSON = OUTPUT_DIR / "trained-policy-evaluation-results.json"
COMPARISON_READINESS_JSON = OUTPUT_DIR / "comparison-readiness-audit.json"
COMPARISON_JSON = OUTPUT_DIR / "baseline-vs-trained-policy-comparison.json"
COMPARISON_MD = OUTPUT_DIR / "baseline-vs-trained-policy-comparison.md"

FEATURE_060_REPORT = Path("artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json")
FEATURE_060_TRAINING_METRICS = Path("artifacts/analysis/full-paper-default-training-campaign-execution/training-metrics.json")
FEATURE_060_EVALUATION_METRICS = Path("artifacts/analysis/full-paper-default-training-campaign-execution/evaluation-metrics.json")
FEATURE_060_CHECKPOINT_METADATA = Path("artifacts/analysis/full-paper-default-training-campaign-execution/checkpoint-metadata.json")
FEATURE_060_RUN_MANIFEST = Path("artifacts/analysis/full-paper-default-training-campaign-execution/run-manifest.json")
FEATURE_060B_REPORT = Path("artifacts/analysis/bind-full-campaign-real-torch-trainer/bind-full-campaign-real-torch-trainer-report.json")
FEATURE_058_REPORT = Path("artifacts/analysis/evaluation-trace-bank-baseline-harness/evaluation-trace-bank-baseline-harness-report.json")

APPROVED_PATH_PREFIXES = (
    "specs/061-campaign-integrity-evaluation-comparison-batch/",
    "src/analysis/campaign_integrity_evaluation_comparison_batch/",
    "tests/unit/test_campaign_integrity_evaluation_comparison_batch",
    "tests/integration/test_campaign_integrity_evaluation_comparison_batch",
    "artifacts/analysis/campaign-integrity-evaluation-comparison-batch/",
)
FORBIDDEN_PATH_PREFIXES = (
    ".specify/feature.json",
    "AGENTS.md",
    "src/environment/",
    "src/policies/",
    "artifacts/analysis/full-paper-default-training-campaign-execution/",
    "artifacts/analysis/bind-full-campaign-real-torch-trainer/",
    "artifacts/analysis/evaluation-trace-bank-baseline-harness/",
)
DEPENDENCY_FILE_NAMES = {".gitignore", "pyproject.toml", "requirements.txt", "requirements-dev.txt", "Pipfile.lock", "poetry.lock", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"}
REQUIRED_TOP_LEVEL_FIELDS = (
    "feature_id",
    "batch_items_covered",
    "prerequisite_tags_verified",
    "feature_060_verified",
    "campaign_integrity_summary",
    "baseline_evaluation_summary",
    "trained_policy_evaluation_summary",
    "comparison_readiness_summary",
    "comparison_report_summary",
    "artifact_manifest_summary",
    "safety_summary",
    "remaining_blockers",
    "recommended_next_feature",
    "final_verdict",
)
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
    "train_eval_separation",
    "baseline_policy_metrics",
)


@dataclass(frozen=True, slots=True)
class CampaignIntegrityEvaluationComparisonBatchConfig:
    output_dir: Path = OUTPUT_DIR
