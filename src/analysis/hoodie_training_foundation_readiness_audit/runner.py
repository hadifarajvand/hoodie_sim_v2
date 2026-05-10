from __future__ import annotations

from pathlib import Path
import json

from .gates import REQUIRED_SOURCE_ARTIFACTS, validate_feature_gates
from .readiness import classify_readiness
from .report import DEFAULT_OUTPUT_DIR, ReadinessAuditReport, build_readiness_report, write_readiness_audit_report


HOODIE_READINESS_OUTPUT_DIR = DEFAULT_OUTPUT_DIR


class HoodieTrainingFoundationReadinessAuditRunner:
    def __init__(self, output_dir: Path | str | None = None):
        self.output_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR

    def _load_text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="ignore")

    def _artifact_payloads(self) -> dict[str, object]:
        return {
            "paper_ocr_text": self._load_text(REQUIRED_SOURCE_ARTIFACTS[0][1]),
            "mechanism_registry": json.loads(self._load_text(REQUIRED_SOURCE_ARTIFACTS[1][1])),
            "differential_audit": json.loads(self._load_text(REQUIRED_SOURCE_ARTIFACTS[2][1])),
            "mechanism_repair_summary": json.loads(self._load_text(REQUIRED_SOURCE_ARTIFACTS[3][1])),
            "controlled_sweeps": json.loads(self._load_text(REQUIRED_SOURCE_ARTIFACTS[4][1])),
            "baseline_fairness_rebuild": json.loads(self._load_text(REQUIRED_SOURCE_ARTIFACTS[5][1])),
            "baseline_rebuild_sensitivity_audit": json.loads(self._load_text(REQUIRED_SOURCE_ARTIFACTS[6][1])),
        }

    def run(self) -> ReadinessAuditReport:
        source_gate_status = validate_feature_gates(*[path for _name, path in REQUIRED_SOURCE_ARTIFACTS]).to_dict()
        payloads = self._artifact_payloads()
        audit = classify_readiness(source_gate_status, payloads)
        report = build_readiness_report(
            audit,
            source_gate_status=source_gate_status,
            included_source_artifacts=[str(path) for _name, path in REQUIRED_SOURCE_ARTIFACTS],
        )
        write_readiness_audit_report(report, self.output_dir)
        return report


def run_hoodie_training_foundation_readiness_audit(output_dir: Path | str | None = None) -> ReadinessAuditReport:
    return HoodieTrainingFoundationReadinessAuditRunner(output_dir=output_dir).run()
