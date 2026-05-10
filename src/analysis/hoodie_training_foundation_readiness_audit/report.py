from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import json
from typing import Any

from .readiness import ReadinessAudit


DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/hoodie-training-foundation-readiness-audit")
JSON_FILENAME = "hoodie-training-foundation-readiness-audit.json"
MARKDOWN_FILENAME = "hoodie-training-foundation-readiness-audit.md"
CSV_FILENAME = "hoodie-training-foundation-readiness-audit.csv"


def _json_dump(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


@dataclass(slots=True)
class ReadinessAuditReport:
    metadata: dict[str, Any]
    source_gate_status: dict[str, Any]
    readiness_dimensions: list[dict[str, Any]]
    included_source_artifacts: list[str]
    mechanism_gaps: list[dict[str, Any]]
    blockers: list[str]
    verdict: str
    limitations: list[str]
    disclaimers: list[str]
    reproducibility_details: dict[str, Any]

    def to_dict(self) -> dict[str, object]:
        return {
            "metadata": dict(self.metadata),
            "source_gate_status": dict(self.source_gate_status),
            "readiness_dimensions": list(self.readiness_dimensions),
            "included_source_artifacts": list(self.included_source_artifacts),
            "mechanism_gaps": list(self.mechanism_gaps),
            "blockers": list(self.blockers),
            "verdict": self.verdict,
            "limitations": list(self.limitations),
            "disclaimers": list(self.disclaimers),
            "reproducibility_details": dict(self.reproducibility_details),
        }


def render_markdown(report: ReadinessAuditReport) -> str:
    payload = report.to_dict()
    lines: list[str] = []
    lines.append("# HOODIE Training Foundation Readiness Audit")
    lines.append("")
    lines.append("## Verdict")
    lines.append(f"- **{payload['verdict']}**")
    lines.append("")
    lines.append("## Metadata")
    for key, value in payload["metadata"].items():
        lines.append(f"- **{key}**: {value}")
    lines.append("")
    lines.append("## Source Gate Status")
    lines.append(f"- **passed**: {payload['source_gate_status'].get('passed')}")
    for item in payload["source_gate_status"].get("checks", []):
        lines.append(f"- **{item['artifact']}** ({item['path']}): valid={item['valid']} details={item['details']}")
    lines.append("")
    lines.append("## Included Source Artifacts")
    for artifact in payload["included_source_artifacts"]:
        lines.append(f"- {artifact}")
    lines.append("")
    lines.append("## Readiness Dimensions")
    for dimension in payload["readiness_dimensions"]:
        lines.append(f"- **{dimension['name']}**: supported={dimension['supported']} evidence={dimension['evidence_source']}")
        for note in dimension["blocker_notes"]:
            lines.append(f"  - {note}")
    lines.append("")
    lines.append("## Mechanism Gaps")
    for gap in payload["mechanism_gaps"]:
        lines.append(f"- **{gap['family']}**: {gap['gap_type']} ({gap['severity']})")
        for evidence in gap["evidence"]:
            lines.append(f"  - {evidence}")
    lines.append("")
    lines.append("## Blockers")
    for blocker in payload["blockers"]:
        lines.append(f"- {blocker}")
    lines.append("")
    lines.append("## Limitations")
    for item in payload["limitations"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Disclaimers")
    for item in payload["disclaimers"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Reproducibility")
    for key, value in payload["reproducibility_details"].items():
        lines.append(f"- **{key}**: {value}")
    lines.append("")
    return "\n".join(lines)


def write_readiness_audit_report(report: ReadinessAuditReport, output_dir: Path | str | None = None) -> tuple[Path, Path]:
    target_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    json_path = target_dir / JSON_FILENAME
    markdown_path = target_dir / MARKDOWN_FILENAME
    csv_path = target_dir / CSV_FILENAME
    json_path.write_text(_json_dump(report.to_dict()), encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name", "supported", "evidence_source"])
        writer.writeheader()
        for item in report.readiness_dimensions:
            writer.writerow({"name": item["name"], "supported": item["supported"], "evidence_source": item["evidence_source"]})
    return json_path, markdown_path


def build_readiness_report(audit: ReadinessAudit, source_gate_status: dict[str, Any], included_source_artifacts: list[str]) -> ReadinessAuditReport:
    return ReadinessAuditReport(
        metadata={
            "feature_id": "023-training-foundation-readiness-audit",
            "generated_by": "hoodie_training_foundation_readiness_audit",
            "deterministic": True,
            "source_refs": [
                "specs/023-training-foundation-readiness-audit/spec.md",
                "specs/023-training-foundation-readiness-audit/plan.md",
                "specs/023-training-foundation-readiness-audit/research.md",
                "specs/023-training-foundation-readiness-audit/data-model.md",
                "specs/023-training-foundation-readiness-audit/quickstart.md",
                "resources/papers/hoodie/ocr/merged.tex",
                "artifacts/analysis/paper-mechanism-registry/paper-mechanism-registry.json",
                "artifacts/analysis/differential-environment-audit/differential-audit.json",
                "artifacts/analysis/mechanism-repair/repair-summary.json",
                "artifacts/analysis/controlled-mechanistic-sweeps/controlled-mechanistic-sweeps.json",
                "artifacts/analysis/baseline-fairness-rebuild/baseline-fairness-rebuild.json",
                "artifacts/analysis/baseline-rebuild-sensitivity-audit/baseline-rebuild-sensitivity-audit.json",
            ],
        },
        source_gate_status=source_gate_status,
        readiness_dimensions=[dimension.to_dict() for dimension in audit.dimensions],
        included_source_artifacts=included_source_artifacts,
        mechanism_gaps=[gap.to_dict() for gap in audit.mechanism_gaps],
        blockers=list(audit.blockers),
        verdict=audit.verdict,
        limitations=list(audit.limitations),
        disclaimers=[
            "No DRL training, neural-network code, or trainer implementation was added.",
            "No policy redesign, metric change, or simulator behavior change was introduced.",
            "This is not a paper-validity or paper-completeness claim.",
        ],
        reproducibility_details={
            "approved_interpreter": "/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python",
            "deterministic_ordering": "gates -> readiness dimensions -> mechanism gaps -> verdict -> report",
            "output_dir": str(DEFAULT_OUTPUT_DIR),
            "csv_optional": True,
        },
    )
