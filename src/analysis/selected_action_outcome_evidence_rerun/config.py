from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

FEATURE_ID = "052-selected-action-outcome-evidence-rerun"
DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/selected-action-outcome-evidence-rerun")
DEFAULT_JSON_FILENAME = "selected-action-outcome-evidence-rerun-report.json"
DEFAULT_MARKDOWN_FILENAME = "selected-action-outcome-evidence-rerun-report.md"

PRIOR_ARTIFACTS = {
    "legality_evidence_expansion": Path("artifacts/analysis/legality-evidence-expansion/legality-evidence-report.json"),
    "exposure_matrix_paper_mechanism_alignment": Path("artifacts/analysis/exposure-matrix-paper-mechanism-alignment/exposure-matrix-paper-mechanism-report.json"),
    "selected_action_family_per_action_outcome_evidence": Path("artifacts/analysis/selected-action-family-per-action-outcome-evidence/selected-action-family-outcome-evidence-report.json"),
    "passive_selected_action_trace_repair": Path("artifacts/analysis/passive-selected-action-trace-repair/passive-selected-action-trace-repair-report.json"),
}


@dataclass(frozen=True, slots=True)
class SelectedActionOutcomeEvidenceRerunConfig:
    episode_length: int = 3
    trace_seed: int = 7
    trace_policy_name: str = "selected_action_outcome_evidence_rerun_probe"
    output_dir: Path = DEFAULT_OUTPUT_DIR
