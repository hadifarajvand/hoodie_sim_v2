from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

FEATURE_ID = "065-paper-faithful-state-action-space-batch"
BRANCH_NAME = "065-paper-faithful-state-action-space-batch"
BASE_BRANCH = "main"
READY_NEXT_FEATURE = "Feature 066 — Distributed Multi-Agent HOODIE Training Batch"

OUTPUT_DIR = Path("artifacts/analysis/paper-faithful-state-action-space-batch")
REPORT_JSON = OUTPUT_DIR / "paper-faithful-state-action-space-batch-report.json"
REPORT_MD = OUTPUT_DIR / "paper-faithful-state-action-space-batch-report.md"
PAPER_STATE_CONTRACT_JSON = OUTPUT_DIR / "paper-state-contract.json"
PAPER_ACTION_SPACE_CONTRACT_JSON = OUTPUT_DIR / "paper-action-space-contract.json"
PAPER_LEGAL_MASK_CONTRACT_JSON = OUTPUT_DIR / "paper-legal-mask-contract.json"
PAPER_LOAD_HISTORY_CONTRACT_JSON = OUTPUT_DIR / "paper-load-history-contract.json"
MIGRATION_READINESS_JSON = OUTPUT_DIR / "migration-readiness-for-feature-066.json"

FEATURE_064_REPORT = Path("artifacts/analysis/final-review-release-gate-batch/final-review-release-gate-batch-report.json")
APPROVED_REGISTRY = Path("resources/papers/hoodie/recovered/user-approved-assumption-registry.json")

APPROVED_PATH_PREFIXES = (
    "specs/065-paper-faithful-state-action-space-batch/",
    "src/analysis/paper_faithful_state_action_space_batch/",
    "src/environment/paper_state.py",
    "src/environment/paper_action_space.py",
    "src/environment/paper_load_history.py",
    "src/environment/paper_lstm_forecast.py",
    "tests/unit/test_paper_faithful_state_action_space_batch",
    "tests/unit/test_paper_state_vector.py",
    "tests/unit/test_paper_action_space.py",
    "tests/unit/test_paper_load_history.py",
    "tests/integration/test_paper_faithful_state_action_space_batch",
    "artifacts/analysis/paper-faithful-state-action-space-batch/",
)
FORBIDDEN_PATH_PREFIXES = (
    ".specify/feature.json",
    "AGENTS.md",
    "src/policies/",
    "artifacts/analysis/final-review-release-gate-batch/",
    "artifacts/analysis/results-export-reproducibility-documentation-batch/",
    "artifacts/analysis/multi-seed-campaign-ablation-batch/",
    "artifacts/analysis/campaign-integrity-evaluation-comparison-batch/",
    "artifacts/analysis/full-paper-default-training-campaign-execution/",
)
DEPENDENCY_FILE_NAMES = {".gitignore", "pyproject.toml", "requirements.txt", "requirements-dev.txt", "Pipfile.lock", "poetry.lock", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"}
REQUIRED_TOP_LEVEL_FIELDS = (
    "feature_id",
    "batch_items_covered",
    "feature_064_verified",
    "paper_state_contract_summary",
    "waiting_time_summary",
    "public_queue_vector_summary",
    "load_history_summary",
    "forecast_input_summary",
    "destination_action_space_summary",
    "legal_mask_summary",
    "compatibility_summary",
    "safety_summary",
    "remaining_blockers",
    "recommended_next_feature",
    "final_verdict",
)

@dataclass(frozen=True, slots=True)
class PaperFaithfulStateActionSpaceBatchConfig:
    output_dir: Path = OUTPUT_DIR
