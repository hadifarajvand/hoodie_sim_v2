from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

FEATURE_ID = "049-exposure-matrix-paper-mechanism-alignment"

FEATURE_043_REPORT = Path("artifacts/analysis/task-completion-lifecycle-formula-audit/completion-lifecycle-audit-report.json")
FEATURE_044_REPORT = Path("artifacts/analysis/passive-runtime-lifecycle-trace-instrumentation/lifecycle-trace-instrumentation-report.json")
FEATURE_045_REPORT = Path("artifacts/analysis/completion-root-cause-diagnosis/completion-root-cause-report.json")
FEATURE_046_REPORT = Path("artifacts/analysis/load-admission-action-exposure-review/load-admission-action-exposure-report.json")
FEATURE_047_REPORT = Path("artifacts/analysis/exposure-matrix-review/exposure-matrix-report.json")
FEATURE_048_REPORT = Path("artifacts/analysis/legality-evidence-expansion/legality-evidence-report.json")

DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/exposure-matrix-paper-mechanism-alignment")


@dataclass(frozen=True, slots=True)
class ExposureMatrixPaperMechanismConfig:
    feature_id: str = FEATURE_ID
    output_dir: Path = DEFAULT_OUTPUT_DIR
    feature_043_report: Path = FEATURE_043_REPORT
    feature_044_report: Path = FEATURE_044_REPORT
    feature_045_report: Path = FEATURE_045_REPORT
    feature_046_report: Path = FEATURE_046_REPORT
    feature_047_report: Path = FEATURE_047_REPORT
    feature_048_report: Path = FEATURE_048_REPORT
    no_runtime_repair: bool = True
    no_training: bool = True
    no_optimizer_step: bool = True
    no_replay_training: bool = True
    no_target_update_execution: bool = True

    def __post_init__(self) -> None:
        if self.feature_id != FEATURE_ID:
            raise ValueError("feature_id must equal 049-exposure-matrix-paper-mechanism-alignment")
        if self.no_runtime_repair is not True:
            raise ValueError("no_runtime_repair must remain true")
        if self.no_training is not True:
            raise ValueError("no_training must remain true")
        if self.no_optimizer_step is not True:
            raise ValueError("no_optimizer_step must remain true")
        if self.no_replay_training is not True:
            raise ValueError("no_replay_training must remain true")
        if self.no_target_update_execution is not True:
            raise ValueError("no_target_update_execution must remain true")
