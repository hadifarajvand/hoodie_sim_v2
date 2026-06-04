from __future__ import annotations

import argparse
import csv
import io
import json
import subprocess
from pathlib import Path
from typing import Any

from .aggregation import aggregate_by_policy
from .config import DEFAULT_OUTPUT_DIR, EvaluationConfig, FEATURE_NAME, POLICY_HOODIE, REQUIRED_POLICIES
from .model import Feature083Report, RankingRow
from .report import build_execution_rows, build_feature_085_report, render_feature_085_report


RAW_ROWS_JSON = "raw_rows.json"
RAW_ROWS_CSV = "raw_rows.csv"
AGGREGATE_BY_POLICY_JSON = "aggregate_by_policy.json"
AGGREGATE_BY_POLICY_CSV = "aggregate_by_policy.csv"
RANKING_BY_METRIC_JSON = "ranking_by_metric.json"
RANKING_BY_METRIC_CSV = "ranking_by_metric.csv"
REPORT_JSON = "feature_085_audit_report.json"
REPORT_MD = "feature_085_audit_report.md"
EXECUTION_MANIFEST_JSON = "execution_manifest.json"


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def _dump_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(_json_safe(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _csv_value(value: Any) -> str | int | float | bool:
    if value is None:
        return ""
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(_json_safe(value), sort_keys=True)
    return value


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _csv_value(row.get(key)) for key in fieldnames})
        handle.write(buffer.getvalue().replace("\r\n", "\n").replace("\r", "\n"))


def _git_output(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def _repo_identity() -> dict[str, str]:
    branch = _git_output("branch", "--show-current")
    local_head_sha = _git_output("rev-parse", "HEAD")
    remote_ref = f"origin/{branch}"
    try:
        remote_head_sha = _git_output("rev-parse", remote_ref)
    except subprocess.CalledProcessError:
        remote_head_sha = local_head_sha
    return {
        "branch": branch,
        "local_head_sha": local_head_sha,
        "remote_head_sha": remote_head_sha,
        "sha_equality": local_head_sha == remote_head_sha,
    }


def _flatten_raw_rows(outcomes_by_key: dict[tuple[str, str, str, str, int], tuple[Any, ...]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key in sorted(outcomes_by_key):
        for outcome in outcomes_by_key[key]:
            rows.append(outcome.to_dict())
    return rows


def _ranking_rows_to_dict(ranking_tables: dict[str, tuple[RankingRow, ...]]) -> dict[str, list[dict[str, Any]]]:
    return {metric: [row.to_dict() for row in rows] for metric, rows in sorted(ranking_tables.items())}


def _metric_rows_differ(left: Any, right: Any) -> bool:
    if left is None or right is None:
        return False
    comparable_fields = (
        "completed_count",
        "dropped_timeout_count",
        "dropped_unavailable_count",
        "deadline_violation_count",
        "illegal_action_rejection_count",
        "task_completion_delay",
        "task_drop_ratio",
        "average_reward",
        "total_reward",
        "completion_rate",
        "timeout_drop_rate",
        "unavailable_drop_rate",
        "deadline_violation_rate",
        "throughput",
        "queue_stability_score",
    )
    return any(getattr(left, field) != getattr(right, field) for field in comparable_fields)


def _metric_differences(left: Any, right: Any) -> list[str]:
    if left is None or right is None:
        return []
    fields = (
        "task_completion_delay",
        "task_drop_ratio",
        "average_reward",
        "total_reward",
        "completion_rate",
        "timeout_drop_rate",
        "unavailable_drop_rate",
        "deadline_violation_rate",
        "throughput",
        "queue_stability_score",
        "illegal_action_rejection_count",
    )
    return [field for field in fields if getattr(left, field) != getattr(right, field)]


def _artifact_markdown(report: Feature083Report, *, output_dir: Path, raw_row_count: int, manifest_path: Path) -> str:
    lines = [
        "# Feature 085 HOODIE Baseline Fidelity Audit Artifact Bundle",
        "",
        f"- output_dir: `{output_dir}`",
        f"- raw_row_count: `{raw_row_count}`",
        f"- policies: `{len(report.policy_coverage)}`",
        f"- scenarios: `{len(report.scenario_coverage)}`",
        f"- metrics: `{len(report.metric_coverage)}`",
        f"- compatibility_mode_used: `{report.compatibility_mode_used}`",
        "",
        "## Generated Files",
        f"- `{RAW_ROWS_JSON}`",
        f"- `{RAW_ROWS_CSV}`",
        f"- `{AGGREGATE_BY_POLICY_JSON}`",
        f"- `{AGGREGATE_BY_POLICY_CSV}`",
        f"- `{RANKING_BY_METRIC_JSON}`",
        f"- `{RANKING_BY_METRIC_CSV}`",
        f"- `{REPORT_JSON}`",
        f"- `{REPORT_MD}`",
        f"- `{EXECUTION_MANIFEST_JSON}`",
        "",
        "## Compatibility-Mode Policies",
    ]
    compatibility = [row.policy for row in report.policy_coverage if row.compatibility_mode_used]
    if compatibility:
        lines.extend(f"- {policy}" for policy in compatibility)
    else:
        lines.append("- no compatibility-mode policies remain")
    lines.append("")
    lines.append(render_feature_085_report(report))
    lines.append("")
    lines.append("## Manifest")
    lines.append(f"- `{manifest_path.name}`")
    return "\n".join(lines) + "\n"


def _execution_manifest(report: Feature083Report, *, config: EvaluationConfig, raw_row_count: int, output_dir: Path) -> dict[str, Any]:
    repo_identity = _repo_identity()
    rows_by_policy = {row.policy: row for row in report.summary_rows}
    identity_proof = {
        "hoodie_vs_ro": {
            "different": _metric_rows_differ(rows_by_policy.get("HOODIE"), rows_by_policy.get("RO")),
            "metrics": _metric_differences(rows_by_policy.get("HOODIE"), rows_by_policy.get("RO")),
        },
        "hoodie_vs_flc": {
            "different": _metric_rows_differ(rows_by_policy.get("HOODIE"), rows_by_policy.get("FLC")),
            "metrics": _metric_differences(rows_by_policy.get("HOODIE"), rows_by_policy.get("FLC")),
        },
        "hoodie_vs_vo": {
            "different": _metric_rows_differ(rows_by_policy.get("HOODIE"), rows_by_policy.get("VO")),
            "metrics": _metric_differences(rows_by_policy.get("HOODIE"), rows_by_policy.get("VO")),
        },
        "hoodie_vs_ho": {
            "different": _metric_rows_differ(rows_by_policy.get("HOODIE"), rows_by_policy.get("HO")),
            "metrics": _metric_differences(rows_by_policy.get("HOODIE"), rows_by_policy.get("HO")),
        },
        "hoodie_vs_bco": {
            "different": _metric_rows_differ(rows_by_policy.get("HOODIE"), rows_by_policy.get("BCO")),
            "metrics": _metric_differences(rows_by_policy.get("HOODIE"), rows_by_policy.get("BCO")),
        },
        "hoodie_vs_mleo": {
            "different": _metric_rows_differ(rows_by_policy.get("HOODIE"), rows_by_policy.get("MLEO")),
            "metrics": _metric_differences(rows_by_policy.get("HOODIE"), rows_by_policy.get("MLEO")),
        },
    }
    generated_files = [
        RAW_ROWS_JSON,
        RAW_ROWS_CSV,
        AGGREGATE_BY_POLICY_JSON,
        AGGREGATE_BY_POLICY_CSV,
        RANKING_BY_METRIC_JSON,
        RANKING_BY_METRIC_CSV,
        REPORT_JSON,
        REPORT_MD,
        EXECUTION_MANIFEST_JSON,
    ]
    return {
        "feature": "085",
        "feature_name": FEATURE_NAME,
        **repo_identity,
        "output_dir": str(output_dir),
        "generated_files": generated_files,
        "raw_row_count": raw_row_count,
        "policy_count": len(config.policies),
        "scenario_count": len(config.scenarios),
        "metric_count": len(report.metric_coverage),
        "workloads": list(config.workloads),
        "deadline_pressures": list(config.deadline_pressures),
        "seeds": list(config.seeds),
        "claim_boundary": list(report.claim_boundary),
        "scope_proof": list(report.scope_proof),
        "policy_action_evidence": list(report.policy_action_evidence),
        "compatibility_mode_policies": [row.policy for row in report.policy_coverage if row.compatibility_mode_used],
        "identity_proof": identity_proof,
        "policy_coverage": [row.to_dict() for row in report.policy_coverage],
        "scenario_coverage": [row.to_dict() for row in report.scenario_coverage],
        "metric_coverage": [row.to_dict() for row in report.metric_coverage],
        "ranking_metrics": sorted(report.ranking_tables),
        "report_status": report.status,
        "passed": report.passed,
        "readiness_level": report.readiness_level,
    }


def generate_hoodie_runtime_evaluation_artifacts(output_dir: Path | None = None) -> tuple[Feature083Report, dict[str, Path], dict[str, Any]]:
    config = EvaluationConfig(output_dir=Path(output_dir or DEFAULT_OUTPUT_DIR))
    output_dir = config.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    report = build_feature_085_report(config)
    raw_metric_rows, _, outcomes_by_key = build_execution_rows(config)
    aggregate_rows = aggregate_by_policy(raw_metric_rows)
    raw_rows = _flatten_raw_rows(outcomes_by_key)
    ranking_rows = _ranking_rows_to_dict(report.ranking_tables)

    raw_rows_json_path = output_dir / RAW_ROWS_JSON
    raw_rows_csv_path = output_dir / RAW_ROWS_CSV
    aggregate_json_path = output_dir / AGGREGATE_BY_POLICY_JSON
    aggregate_csv_path = output_dir / AGGREGATE_BY_POLICY_CSV
    ranking_json_path = output_dir / RANKING_BY_METRIC_JSON
    ranking_csv_path = output_dir / RANKING_BY_METRIC_CSV
    report_json_path = output_dir / REPORT_JSON
    report_md_path = output_dir / REPORT_MD
    manifest_path = output_dir / EXECUTION_MANIFEST_JSON

    _dump_json(raw_rows_json_path, {"count": len(raw_rows), "rows": raw_rows})
    _write_csv(raw_rows_csv_path, raw_rows)
    _dump_json(aggregate_json_path, {"count": len(aggregate_rows), "rows": [row.to_dict() for row in aggregate_rows]})
    _write_csv(aggregate_csv_path, [row.to_dict() for row in aggregate_rows])
    _dump_json(ranking_json_path, {"metric_count": len(ranking_rows), "ranking_tables": ranking_rows})
    ranking_csv_rows: list[dict[str, Any]] = []
    for metric, rows in ranking_rows.items():
        for row in rows:
            ranking_csv_rows.append({"metric": metric, **row})
    _write_csv(ranking_csv_path, ranking_csv_rows)
    _dump_json(report_json_path, report.to_dict())
    report_md_path.write_text(_artifact_markdown(report, output_dir=output_dir, raw_row_count=len(raw_rows), manifest_path=manifest_path), encoding="utf-8")
    manifest = _execution_manifest(report, config=config, raw_row_count=len(raw_rows), output_dir=output_dir)
    _dump_json(manifest_path, manifest)

    artifact_paths = {
        RAW_ROWS_JSON: raw_rows_json_path,
        RAW_ROWS_CSV: raw_rows_csv_path,
        AGGREGATE_BY_POLICY_JSON: aggregate_json_path,
        AGGREGATE_BY_POLICY_CSV: aggregate_csv_path,
        RANKING_BY_METRIC_JSON: ranking_json_path,
        RANKING_BY_METRIC_CSV: ranking_csv_path,
        REPORT_JSON: report_json_path,
        REPORT_MD: report_md_path,
        EXECUTION_MANIFEST_JSON: manifest_path,
    }
    return report, artifact_paths, manifest


def validate_hoodie_runtime_evaluation_artifacts(output_dir: Path | None = None) -> dict[str, Any]:
    output_dir = Path(output_dir or DEFAULT_OUTPUT_DIR)
    required = (
        RAW_ROWS_JSON,
        RAW_ROWS_CSV,
        AGGREGATE_BY_POLICY_JSON,
        AGGREGATE_BY_POLICY_CSV,
        RANKING_BY_METRIC_JSON,
        RANKING_BY_METRIC_CSV,
        REPORT_JSON,
        REPORT_MD,
        EXECUTION_MANIFEST_JSON,
    )
    missing = [name for name in required if not (output_dir / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing Feature 085 artifacts: {', '.join(missing)}")
    manifest = json.loads((output_dir / EXECUTION_MANIFEST_JSON).read_text(encoding="utf-8"))
    if manifest.get("generated_files") != list(required):
        raise ValueError("Feature 085 execution manifest generated_files does not match the required artifact set")
    if manifest.get("feature") != "085":
        raise ValueError("Feature 085 execution manifest must declare feature id 085")
    if manifest.get("feature_name") != FEATURE_NAME:
        raise ValueError("Feature 085 execution manifest must declare the canonical feature name")
    aggregate_payload = json.loads((output_dir / AGGREGATE_BY_POLICY_JSON).read_text(encoding="utf-8"))
    rows = {row["policy"]: row for row in aggregate_payload.get("rows", [])}
    if set(rows) != set(REQUIRED_POLICIES):
        raise ValueError("Feature 085 aggregate_by_policy.json must contain exactly the required paper policies")
    for baseline in (policy for policy in REQUIRED_POLICIES if policy != POLICY_HOODIE):
        if rows.get(baseline) is None:
            raise ValueError(f"Feature 085 aggregate_by_policy.json does not contain {baseline}")
    return {
        "output_dir": str(output_dir),
        "validated": True,
        "missing": missing,
        "manifest": manifest,
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate or validate Feature 085 runtime evaluation artifacts.")
    parser.add_argument("--write-artifacts", nargs="?", const=str(DEFAULT_OUTPUT_DIR), default=None, metavar="DIR", help="Write Feature 085 artifacts to DIR.")
    parser.add_argument("--validate-artifacts", action="store_true", help="Validate the Feature 085 artifact bundle in the default output directory.")
    parser.add_argument("--artifact-dir", default=None, help="Override the artifact directory used by validation.")
    args = parser.parse_args(argv)

    report = None
    if args.write_artifacts is not None:
        report, _, _ = generate_hoodie_runtime_evaluation_artifacts(Path(args.write_artifacts))
    if args.validate_artifacts:
        validate_hoodie_runtime_evaluation_artifacts(Path(args.artifact_dir) if args.artifact_dir else None)
        if report is None:
            report = build_feature_085_report(EvaluationConfig(output_dir=Path(args.artifact_dir) if args.artifact_dir else DEFAULT_OUTPUT_DIR))
    if report is None:
        report = build_feature_085_report()
    print(render_feature_085_report(report))


if __name__ == "__main__":
    main()
