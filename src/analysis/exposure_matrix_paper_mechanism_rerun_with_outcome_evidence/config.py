from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

FEATURE_ID = "053-exposure-matrix-paper-mechanism-rerun-with-outcome-evidence"
DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/exposure-matrix-paper-mechanism-rerun-with-outcome-evidence")
DEFAULT_JSON_FILENAME = "exposure-matrix-paper-mechanism-rerun-report.json"
DEFAULT_MARKDOWN_FILENAME = "exposure-matrix-paper-mechanism-rerun-report.md"

FEATURE_048_REPORT = Path("artifacts/analysis/legality-evidence-expansion/legality-evidence-report.json")
FEATURE_049_REPORT = Path("artifacts/analysis/exposure-matrix-paper-mechanism-alignment/exposure-matrix-paper-mechanism-report.json")
FEATURE_050_REPORT = Path("artifacts/analysis/selected-action-family-per-action-outcome-evidence/selected-action-family-outcome-evidence-report.json")
FEATURE_051_REPORT = Path("artifacts/analysis/passive-selected-action-trace-repair/passive-selected-action-trace-repair-report.json")
FEATURE_052_REPORT = Path("artifacts/analysis/selected-action-outcome-evidence-rerun/selected-action-outcome-evidence-rerun-report.json")

COMMITTED_INPUT_REPORTS = {
    "048": FEATURE_048_REPORT,
    "049": FEATURE_049_REPORT,
    "050": FEATURE_050_REPORT,
    "051": FEATURE_051_REPORT,
    "052": FEATURE_052_REPORT,
}

READY_NEXT_FEATURE = "Feature 054 — Training Readiness Contract"


@dataclass(frozen=True, slots=True)
class ExposureMatrixPaperMechanismRerunConfig:
    feature_id: str = FEATURE_ID
    output_dir: Path = DEFAULT_OUTPUT_DIR
    feature_048_report: Path = FEATURE_048_REPORT
    feature_049_report: Path = FEATURE_049_REPORT
    feature_050_report: Path = FEATURE_050_REPORT
    feature_051_report: Path = FEATURE_051_REPORT
    feature_052_report: Path = FEATURE_052_REPORT

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 053-exposure-matrix-paper-mechanism-rerun-with-outcome-evidence")
