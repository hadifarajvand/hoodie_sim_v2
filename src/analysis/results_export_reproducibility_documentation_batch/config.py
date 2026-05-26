from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

FEATURE_ID = "063-results-export-reproducibility-documentation-batch"
BRANCH_NAME = "063-results-export-reproducibility-documentation-batch"
BASE_BRANCH = "main"
READY_NEXT_FEATURE = "Feature 064 — Final Review and Release Gate"

OUTPUT_DIR = Path("artifacts/analysis/results-export-reproducibility-documentation-batch")
REPORT_JSON = OUTPUT_DIR / "results-export-reproducibility-documentation-batch-report.json"
REPORT_MD = OUTPUT_DIR / "results-export-reproducibility-documentation-batch-report.md"
FINAL_INTEGRITY_AUDIT_JSON = OUTPUT_DIR / "final-experiment-integrity-audit.json"
RESULTS_TABLE_CSV = OUTPUT_DIR / "results-table-export.csv"
RESULTS_TABLE_MD = OUTPUT_DIR / "results-table-export.md"
FIGURE_DATA_JSON = OUTPUT_DIR / "figure-data-export.json"
REPRODUCIBILITY_PACKAGE_MD = OUTPUT_DIR / "reproducibility-package.md"
FINAL_MECHANISM_DOC_MD = OUTPUT_DIR / "final-mechanism-documentation.md"
FINAL_ARTIFACT_INDEX_JSON = OUTPUT_DIR / "final-artifact-index.json"

FEATURE_062_REPORT = Path("artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-ablation-batch-report.json")
FEATURE_062_RESULTS = Path("artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-campaign-results.json")
FEATURE_062_AGGREGATION = Path("artifacts/analysis/multi-seed-campaign-ablation-batch/multi-seed-aggregation.json")
FEATURE_062_ABLATION = Path("artifacts/analysis/multi-seed-campaign-ablation-batch/ablation-results.json")
FEATURE_061_COMPARISON = Path("artifacts/analysis/campaign-integrity-evaluation-comparison-batch/baseline-vs-trained-policy-comparison.json")
FEATURE_060_REPORT = Path("artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json")

APPROVED_PATH_PREFIXES = (
    "specs/063-results-export-reproducibility-documentation-batch/",
    "src/analysis/results_export_reproducibility_documentation_batch/",
    "tests/unit/test_results_export_reproducibility_documentation_batch",
    "tests/integration/test_results_export_reproducibility_documentation_batch",
    "artifacts/analysis/results-export-reproducibility-documentation-batch/",
)
FORBIDDEN_PATH_PREFIXES = (
    ".specify/feature.json",
    "AGENTS.md",
    "src/environment/",
    "src/policies/",
    "artifacts/analysis/multi-seed-campaign-ablation-batch/",
    "artifacts/analysis/campaign-integrity-evaluation-comparison-batch/",
    "artifacts/analysis/full-paper-default-training-campaign-execution/",
)
DEPENDENCY_FILE_NAMES = {".gitignore", "pyproject.toml", "requirements.txt", "requirements-dev.txt", "Pipfile.lock", "poetry.lock", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"}
REQUIRED_TOP_LEVEL_FIELDS = (
    "feature_id",
    "batch_items_covered",
    "prerequisite_tags_verified",
    "feature_062_verified",
    "final_integrity_audit_summary",
    "results_export_summary",
    "reproducibility_package_summary",
    "mechanism_documentation_summary",
    "artifact_index_summary",
    "claim_boundary_summary",
    "safety_summary",
    "remaining_blockers",
    "recommended_next_feature",
    "final_verdict",
)

@dataclass(frozen=True, slots=True)
class ResultsExportReproducibilityDocumentationBatchConfig:
    output_dir: Path = OUTPUT_DIR
