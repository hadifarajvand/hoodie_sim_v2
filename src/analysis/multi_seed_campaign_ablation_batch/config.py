from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

FEATURE_ID = "062-multi-seed-campaign-ablation-batch"
BRANCH_NAME = "062-multi-seed-campaign-ablation-batch"
BASE_BRANCH = "main"
READY_NEXT_FEATURE = "Feature 063 — Results Export, Reproducibility, and Final Documentation Batch"

OUTPUT_DIR = Path("artifacts/analysis/multi-seed-campaign-ablation-batch")
REPORT_JSON = OUTPUT_DIR / "multi-seed-campaign-ablation-batch-report.json"
REPORT_MD = OUTPUT_DIR / "multi-seed-campaign-ablation-batch-report.md"
MULTI_SEED_GATE_JSON = OUTPUT_DIR / "multi-seed-campaign-gate.json"
MULTI_SEED_RESULTS_JSON = OUTPUT_DIR / "multi-seed-campaign-results.json"
MULTI_SEED_AGGREGATION_JSON = OUTPUT_DIR / "multi-seed-aggregation.json"
ABLATION_GATE_JSON = OUTPUT_DIR / "ablation-gate.json"
ABLATION_RESULTS_JSON = OUTPUT_DIR / "ablation-results.json"

FEATURE_061_REPORT = Path("artifacts/analysis/campaign-integrity-evaluation-comparison-batch/campaign-integrity-evaluation-comparison-batch-report.json")
FEATURE_061_BASELINE_RESULTS = Path("artifacts/analysis/campaign-integrity-evaluation-comparison-batch/baseline-evaluation-results.json")
FEATURE_061_TRAINED_RESULTS = Path("artifacts/analysis/campaign-integrity-evaluation-comparison-batch/trained-policy-evaluation-results.json")
FEATURE_061_COMPARISON_READINESS = Path("artifacts/analysis/campaign-integrity-evaluation-comparison-batch/comparison-readiness-audit.json")
FEATURE_061_COMPARISON_REPORT = Path("artifacts/analysis/campaign-integrity-evaluation-comparison-batch/baseline-vs-trained-policy-comparison.json")
FEATURE_060_REPORT = Path("artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json")
FEATURE_060B_REPORT = Path("artifacts/analysis/bind-full-campaign-real-torch-trainer/bind-full-campaign-real-torch-trainer-report.json")

APPROVED_PATH_PREFIXES = (
    "specs/062-multi-seed-campaign-ablation-batch/",
    "src/analysis/multi_seed_campaign_ablation_batch/",
    "tests/unit/test_multi_seed_campaign_ablation_batch",
    "tests/integration/test_multi_seed_campaign_ablation_batch",
    "artifacts/analysis/multi-seed-campaign-ablation-batch/",
)
FORBIDDEN_PATH_PREFIXES = (
    ".specify/feature.json",
    "AGENTS.md",
    "src/environment/",
    "src/policies/",
    "artifacts/analysis/full-paper-default-training-campaign-execution/",
    "artifacts/analysis/bind-full-campaign-real-torch-trainer/",
    "artifacts/analysis/campaign-integrity-evaluation-comparison-batch/",
)
DEPENDENCY_FILE_NAMES = {".gitignore", "pyproject.toml", "requirements.txt", "requirements-dev.txt", "Pipfile.lock", "poetry.lock", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"}
REQUIRED_TOP_LEVEL_FIELDS = (
    "feature_id",
    "batch_items_covered",
    "prerequisite_tags_verified",
    "feature_061_verified",
    "multi_seed_gate_summary",
    "multi_seed_campaign_summary",
    "multi_seed_aggregation_summary",
    "ablation_gate_summary",
    "ablation_execution_summary",
    "artifact_manifest_summary",
    "safety_summary",
    "remaining_blockers",
    "recommended_next_feature",
    "final_verdict",
)

@dataclass(frozen=True, slots=True)
class MultiSeedCampaignAblationBatchConfig:
    output_dir: Path = OUTPUT_DIR
