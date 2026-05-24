from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

FEATURE_ID = "051-passive-selected-action-trace-repair"
DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/passive-selected-action-trace-repair")
DEFAULT_JSON_FILENAME = "passive-selected-action-trace-repair-report.json"
DEFAULT_MARKDOWN_FILENAME = "passive-selected-action-trace-repair-report.md"

PRIOR_ARTIFACTS = {
    "passive_runtime_lifecycle_trace_instrumentation": Path(
        "artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/lifecycle-trace-instrumentation-report.json"
    ),
    "legality_evidence_expansion": Path("artifacts/analysis/legality-evidence-expansion/legality-evidence-report.json"),
    "exposure_matrix_paper_mechanism_alignment": Path(
        "artifacts/analysis/exposure-matrix-paper-mechanism-alignment/exposure-matrix-paper-mechanism-report.json"
    ),
    "selected_action_family_per_action_outcome_evidence": Path(
        "artifacts/analysis/selected-action-family-per-action-outcome-evidence/selected-action-family-outcome-evidence-report.json"
    ),
}


@dataclass(frozen=True, slots=True)
class PassiveSelectedActionTraceRepairConfig:
    output_dir: Path = DEFAULT_OUTPUT_DIR
    json_filename: str = DEFAULT_JSON_FILENAME
    markdown_filename: str = DEFAULT_MARKDOWN_FILENAME
