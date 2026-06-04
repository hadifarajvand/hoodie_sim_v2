from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path
from typing import Any

from .config import ACTIVE_POLICIES, DEFAULT_OUTPUT_DIR, FEATURE_ID, FEATURE_NAME, INVALID_LABELS, READY_STATUS
from .report import build_feature_086_report, dump_json, render_feature_086_report


MECHANISM_COVERAGE_JSON = "mechanism_coverage.json"
MECHANISM_COVERAGE_CSV = "mechanism_coverage.csv"
SYSTEM_MODEL_GAP_MATRIX_JSON = "system_model_gap_matrix.json"
SYSTEM_MODEL_GAP_MATRIX_MD = "system_model_gap_matrix.md"
METRIC_READINESS_MATRIX_JSON = "metric_readiness_matrix.json"
METRIC_READINESS_MATRIX_MD = "metric_readiness_matrix.md"
SCENARIO_MECHANISM_COVERAGE_JSON = "scenario_mechanism_coverage.json"
TIE_EVIDENCE_JSON = "hoodie_mleo_tie_evidence.json"
REPORT_JSON = "feature_086_system_model_fidelity_report.json"
REPORT_MD = "feature_086_system_model_fidelity_report.md"


def _csv_value(value: Any) -> str | int | float | bool:
    if value is None:
        return ""
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True)
    return value


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: _csv_value(row.get(key)) for key in fieldnames})
    path.write_text(buffer.getvalue().replace("\r\n", "\n").replace("\r", "\n"), encoding="utf-8")


def _validate_active_policy_set(report_payload: dict[str, Any]) -> None:
    if tuple(report_payload.get("active_policies", ())) != ACTIVE_POLICIES:
        raise ValueError("Feature 086 active policies must match the paper-fidelity set exactly")
    invalid_joined = " ".join(report_payload.get("invalid_label_check", ()))
    if any(label in invalid_joined for label in INVALID_LABELS):
        raise ValueError("Feature 086 active outputs must not expose legacy active labels")


def _validate_verdict(report_payload: dict[str, Any]) -> None:
    if report_payload.get("verdict") not in {READY_STATUS, "system_model_fidelity_blocked"}:
        raise ValueError("Feature 086 verdict must be explicit and recognized")
    if report_payload.get("status") != report_payload.get("verdict"):
        raise ValueError("Feature 086 status and verdict must agree")


def generate_feature_086_artifacts(output_dir: Path | None = None) -> tuple[dict[str, Any], dict[str, Path]]:
    output_dir = Path(output_dir or DEFAULT_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    report = build_feature_086_report()
    payload = report.to_dict()

    _validate_active_policy_set(payload)
    _validate_verdict(payload)

    mechanism_rows = [row for row in payload["mechanism_coverage"]]
    gap_rows = [row for row in payload["system_model_gap_matrix"]]
    metric_rows = [row for row in payload["metric_readiness_matrix"]]
    scenario_rows = [row for row in payload["scenario_mechanism_coverage"]]
    tie_evidence = payload["hoodie_mleo_tie_evidence"]

    paths = {
        MECHANISM_COVERAGE_JSON: output_dir / MECHANISM_COVERAGE_JSON,
        MECHANISM_COVERAGE_CSV: output_dir / MECHANISM_COVERAGE_CSV,
        SYSTEM_MODEL_GAP_MATRIX_JSON: output_dir / SYSTEM_MODEL_GAP_MATRIX_JSON,
        SYSTEM_MODEL_GAP_MATRIX_MD: output_dir / SYSTEM_MODEL_GAP_MATRIX_MD,
        METRIC_READINESS_MATRIX_JSON: output_dir / METRIC_READINESS_MATRIX_JSON,
        METRIC_READINESS_MATRIX_MD: output_dir / METRIC_READINESS_MATRIX_MD,
        SCENARIO_MECHANISM_COVERAGE_JSON: output_dir / SCENARIO_MECHANISM_COVERAGE_JSON,
        TIE_EVIDENCE_JSON: output_dir / TIE_EVIDENCE_JSON,
        REPORT_JSON: output_dir / REPORT_JSON,
        REPORT_MD: output_dir / REPORT_MD,
    }

    paths[MECHANISM_COVERAGE_JSON].write_text(dump_json({"count": len(mechanism_rows), "rows": mechanism_rows}), encoding="utf-8")
    _write_csv(paths[MECHANISM_COVERAGE_CSV], mechanism_rows)
    paths[SYSTEM_MODEL_GAP_MATRIX_JSON].write_text(dump_json({"count": len(gap_rows), "rows": gap_rows}), encoding="utf-8")
    gap_md_rows = [
        {
            "mechanism_id": row["mechanism_id"],
            "status": row["status"],
            "required_fix_or_claim_boundary": row["required_fix_or_claim_boundary"],
        }
        for row in gap_rows
    ]
    paths[SYSTEM_MODEL_GAP_MATRIX_MD].write_text(
        "# Feature 086 System Model Gap Matrix\n\n" + _render_simple_table(gap_md_rows) + "\n",
        encoding="utf-8",
    )
    paths[METRIC_READINESS_MATRIX_JSON].write_text(dump_json({"count": len(metric_rows), "rows": metric_rows}), encoding="utf-8")
    metric_md_rows = [
        {
            "metric": row["metric"],
            "classification": row["classification"],
            "status": row["status"],
            "paper_use": row["paper_use"],
        }
        for row in metric_rows
    ]
    paths[METRIC_READINESS_MATRIX_MD].write_text(
        "# Feature 086 Metric Readiness Matrix\n\n" + _render_simple_table(metric_md_rows) + "\n",
        encoding="utf-8",
    )
    paths[SCENARIO_MECHANISM_COVERAGE_JSON].write_text(dump_json({"count": len(scenario_rows), "rows": scenario_rows}), encoding="utf-8")
    paths[TIE_EVIDENCE_JSON].write_text(dump_json(tie_evidence), encoding="utf-8")
    paths[REPORT_JSON].write_text(dump_json(payload), encoding="utf-8")
    paths[REPORT_MD].write_text(render_feature_086_report(report), encoding="utf-8")
    return payload, paths


def _render_simple_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "_No rows._"
    headers = list(rows[0])
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "")) for header in headers) + " |")
    return "\n".join(lines)


def validate_feature_086_artifacts(output_dir: Path | None = None) -> dict[str, Any]:
    output_dir = Path(output_dir or DEFAULT_OUTPUT_DIR)
    required = (
        MECHANISM_COVERAGE_JSON,
        MECHANISM_COVERAGE_CSV,
        SYSTEM_MODEL_GAP_MATRIX_JSON,
        SYSTEM_MODEL_GAP_MATRIX_MD,
        METRIC_READINESS_MATRIX_JSON,
        METRIC_READINESS_MATRIX_MD,
        SCENARIO_MECHANISM_COVERAGE_JSON,
        TIE_EVIDENCE_JSON,
        REPORT_JSON,
        REPORT_MD,
    )
    missing = [name for name in required if not (output_dir / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing Feature 086 artifacts: {', '.join(missing)}")
    report = json.loads((output_dir / REPORT_JSON).read_text(encoding="utf-8"))
    _validate_active_policy_set(report)
    _validate_verdict(report)
    if report.get("feature_id") != FEATURE_ID:
        raise ValueError("Feature 086 report must declare the 086 feature id")
    if report.get("verdict") == READY_STATUS and report.get("blocked_mechanisms"):
        raise ValueError("Ready verdict cannot have blocked mechanisms")
    if not report.get("mechanism_coverage"):
        raise ValueError("Feature 086 report must include mechanism coverage")
    if not report.get("metric_readiness_matrix"):
        raise ValueError("Feature 086 report must include metric readiness coverage")
    return {
        "output_dir": str(output_dir),
        "validated": True,
        "missing": missing,
        "report_status": report.get("status"),
        "verdict": report.get("verdict"),
    }


class HoodieSystemModelFidelityRunner:
    def __init__(self, output_dir: Path | None = None) -> None:
        self.output_dir = Path(output_dir or DEFAULT_OUTPUT_DIR)

    def generate(self) -> dict[str, Any]:
        payload, _ = generate_feature_086_artifacts(self.output_dir)
        return payload

    def validate(self) -> dict[str, Any]:
        return validate_feature_086_artifacts(self.output_dir)


HoodieProposedFidelityRunner = HoodieSystemModelFidelityRunner


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate or validate Feature 086 system-model fidelity artifacts.")
    parser.add_argument("--write-artifacts", nargs="?", const=str(DEFAULT_OUTPUT_DIR), default=None, metavar="DIR", help="Write Feature 086 artifacts to DIR.")
    parser.add_argument("--validate-artifacts", action="store_true", help="Validate the Feature 086 artifact bundle in the selected directory.")
    parser.add_argument("--artifact-dir", default=None, help="Override the artifact directory used by validation.")
    args = parser.parse_args(argv)

    report = None
    if args.write_artifacts is not None:
        report, _ = generate_feature_086_artifacts(Path(args.write_artifacts))
    if args.validate_artifacts:
        validate_feature_086_artifacts(Path(args.artifact_dir) if args.artifact_dir else None)
        if report is None:
            report = build_feature_086_report().to_dict()
    if report is None:
        report = build_feature_086_report().to_dict()
    print(render_feature_086_report(build_feature_086_report()))


if __name__ == "__main__":
    main()
