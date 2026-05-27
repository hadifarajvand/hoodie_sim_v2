from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

FEATURE_ID = "064-final-review-release-gate-batch"
BRANCH_NAME = "064-final-review-release-gate-batch"
BASE_BRANCH = "main"
READY_NEXT_FEATURE = "Release tag creation or thesis/paper writing workflow"
RECOMMENDED_RELEASE_TAG = "hoodie-mechanism-evidence-release-v1"

OUTPUT_DIR = Path("artifacts/analysis/final-review-release-gate-batch")
REPORT_JSON = OUTPUT_DIR / "final-review-release-gate-batch-report.json"
REPORT_MD = OUTPUT_DIR / "final-review-release-gate-batch-report.md"
REPOSITORY_STATE_AUDIT_JSON = OUTPUT_DIR / "final-repository-state-audit.json"
ARTIFACT_COMPLETENESS_JSON = OUTPUT_DIR / "final-artifact-completeness-gate.json"
CLAIM_BOUNDARY_JSON = OUTPUT_DIR / "final-claim-boundary-review.json"
RELEASE_TAG_READINESS_MD = OUTPUT_DIR / "release-tag-readiness-package.md"
HANDOFF_MD = OUTPUT_DIR / "final-handoff-and-next-work.md"

FEATURE_063_REPORT = Path("artifacts/analysis/results-export-reproducibility-documentation-batch/results-export-reproducibility-documentation-batch-report.json")
FEATURE_063_FINAL_AUDIT = Path("artifacts/analysis/results-export-reproducibility-documentation-batch/final-experiment-integrity-audit.json")
FEATURE_063_RESULTS_TABLE_CSV = Path("artifacts/analysis/results-export-reproducibility-documentation-batch/results-table-export.csv")
FEATURE_063_RESULTS_TABLE_MD = Path("artifacts/analysis/results-export-reproducibility-documentation-batch/results-table-export.md")
FEATURE_063_FIGURE_DATA = Path("artifacts/analysis/results-export-reproducibility-documentation-batch/figure-data-export.json")
FEATURE_063_REPRODUCIBILITY = Path("artifacts/analysis/results-export-reproducibility-documentation-batch/reproducibility-package.md")
FEATURE_063_MECHANISM_DOC = Path("artifacts/analysis/results-export-reproducibility-documentation-batch/final-mechanism-documentation.md")
FEATURE_063_ARTIFACT_INDEX = Path("artifacts/analysis/results-export-reproducibility-documentation-batch/final-artifact-index.json")

APPROVED_PATH_PREFIXES = (
    "specs/064-final-review-release-gate-batch/",
    "src/analysis/final_review_release_gate_batch/",
    "tests/unit/test_final_review_release_gate_batch",
    "tests/integration/test_final_review_release_gate_batch",
    "artifacts/analysis/final-review-release-gate-batch/",
)
FORBIDDEN_PATH_PREFIXES = (
    ".specify/feature.json",
    "AGENTS.md",
    "src/environment/",
    "src/policies/",
    "artifacts/analysis/results-export-reproducibility-documentation-batch/",
    "artifacts/analysis/multi-seed-campaign-ablation-batch/",
    "artifacts/analysis/campaign-integrity-evaluation-comparison-batch/",
    "artifacts/analysis/full-paper-default-training-campaign-execution/",
)
DEPENDENCY_FILE_NAMES = {".gitignore", "pyproject.toml", "requirements.txt", "requirements-dev.txt", "Pipfile.lock", "poetry.lock", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"}
REQUIRED_TOP_LEVEL_FIELDS = (
    "feature_id",
    "batch_items_covered",
    "prerequisite_tags_verified",
    "feature_063_verified",
    "repository_state_audit_summary",
    "artifact_completeness_summary",
    "claim_boundary_review_summary",
    "release_tag_readiness_summary",
    "handoff_summary",
    "safety_summary",
    "remaining_blockers",
    "recommended_next_feature",
    "final_verdict",
)

@dataclass(frozen=True, slots=True)
class FinalReviewReleaseGateBatchConfig:
    output_dir: Path = OUTPUT_DIR
