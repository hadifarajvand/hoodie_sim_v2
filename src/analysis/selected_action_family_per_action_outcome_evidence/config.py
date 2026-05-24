from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

FEATURE_ID = "050-selected-action-family-per-action-outcome-evidence"
DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/selected-action-family-per-action-outcome-evidence")
DEFAULT_JSON_FILENAME = "selected-action-family-outcome-evidence-report.json"
DEFAULT_MARKDOWN_FILENAME = "selected-action-family-outcome-evidence-report.md"

PRIOR_ARTIFACTS = {
    "passive_runtime_lifecycle_trace_instrumentation": Path("artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/lifecycle-trace-instrumentation-report.json"),
    "legality_evidence_expansion": Path("artifacts/analysis/legality-evidence-expansion/legality-evidence-report.json"),
    "exposure_matrix_paper_mechanism_alignment": Path("artifacts/analysis/exposure-matrix-paper-mechanism-alignment/exposure-matrix-paper-mechanism-report.json"),
}


@dataclass(frozen=True, slots=True)
class SelectedActionOutcomeEvidenceConfig:
    output_dir: Path = DEFAULT_OUTPUT_DIR
    json_filename: str = DEFAULT_JSON_FILENAME
    markdown_filename: str = DEFAULT_MARKDOWN_FILENAME
