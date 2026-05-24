from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

FEATURE_ID = "054-training-readiness-contract"
DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/training-readiness-contract")
DEFAULT_JSON_FILENAME = "training-readiness-contract-report.json"
DEFAULT_MARKDOWN_FILENAME = "training-readiness-contract-report.md"

FEATURE_048_REPORT = Path("artifacts/analysis/legality-evidence-expansion/legality-evidence-report.json")
FEATURE_049_REPORT = Path("artifacts/analysis/exposure-matrix-paper-mechanism-alignment/exposure-matrix-paper-mechanism-report.json")
FEATURE_050_REPORT = Path("artifacts/analysis/selected-action-family-per-action-outcome-evidence/selected-action-family-outcome-evidence-report.json")
FEATURE_051_REPORT = Path("artifacts/analysis/passive-selected-action-trace-repair/passive-selected-action-trace-repair-report.json")
FEATURE_052_REPORT = Path("artifacts/analysis/selected-action-outcome-evidence-rerun/selected-action-outcome-evidence-rerun-report.json")
FEATURE_053_REPORT = Path("artifacts/analysis/exposure-matrix-paper-mechanism-rerun-with-outcome-evidence/exposure-matrix-paper-mechanism-rerun-report.json")
FEATURE_038_REPORT = Path("artifacts/analysis/training-foundation-contract/training-foundation-contract-report.json")
FEATURE_040_REPORT = Path("artifacts/analysis/smoke-training/smoke-training-report.json")
FEATURE_041_REPORT = Path("artifacts/analysis/full-training-reproduction-campaign/training-campaign-report.json")
FEATURE_042_REPORT = Path("artifacts/analysis/paper-default-terminal-exposure-probe/terminal-exposure-report.json")

COMMITTED_INPUT_REPORTS = {
    "048": FEATURE_048_REPORT,
    "049": FEATURE_049_REPORT,
    "050": FEATURE_050_REPORT,
    "051": FEATURE_051_REPORT,
    "052": FEATURE_052_REPORT,
    "053": FEATURE_053_REPORT,
}

EXPECTED_FEATURE_IDS = {
    "048": "048-legality-evidence-expansion",
    "049": "049-exposure-matrix-paper-mechanism-alignment",
    "050": "050-selected-action-family-per-action-outcome-evidence",
    "051": "051-passive-selected-action-trace-repair",
    "052": "052-selected-action-outcome-evidence-rerun",
    "053": "053-exposure-matrix-paper-mechanism-rerun-with-outcome-evidence",
}

READY_NEXT_FEATURE = "Feature 055 — Paper-Default Training Smoke Run"

FEATURE_053_PREREQUISITE_TAG = "053-exposure-matrix-paper-mechanism-rerun-with-outcome-evidence-complete^{}"
FEATURE_054A_PREREQUISITE_TAG = "054a-speckit-local-state-hygiene-complete^{}"

DEPENDENCY_FILE_NAMES = {
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "requirements-test.txt",
    "poetry.lock",
    "uv.lock",
    "Pipfile",
    "Pipfile.lock",
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "Cargo.toml",
    "Cargo.lock",
    "setup.py",
    "setup.cfg",
}


@dataclass(frozen=True, slots=True)
class TrainingReadinessContractConfig:
    feature_id: str = FEATURE_ID
    output_dir: Path = DEFAULT_OUTPUT_DIR
    feature_048_report: Path = FEATURE_048_REPORT
    feature_049_report: Path = FEATURE_049_REPORT
    feature_050_report: Path = FEATURE_050_REPORT
    feature_051_report: Path = FEATURE_051_REPORT
    feature_052_report: Path = FEATURE_052_REPORT
    feature_053_report: Path = FEATURE_053_REPORT

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 054-training-readiness-contract")
