from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path
from typing import Any

from .aggregation import aggregate_by_policy
from .config import EvaluationConfig, REQUIRED_POLICIES, REQUIRED_SCENARIOS
from .model import Feature081Report, RankingRow
from .report import build_execution_rows, build_feature_081_report, render_feature_081_report


DEFAULT_OUTPUT_DIR = Path("artifacts/feature_081_evaluation_baseline")
RAW_ROWS_JSON = "raw_rows.json"
RAW_ROWS_CSV = "raw_rows.csv"
AGGREGATE_BY_POLICY_JSON = "aggregate_by_policy.json"
AGGREGATE_BY_POLICY_CSV = "aggregate_by_policy.csv"
RANKING_BY_METRIC_JSON = "ranking_by_metric.json"
RANKING_BY_METRIC_CSV = "ranking_by_metric.csv"
REPORT_MD = "feature_081_evaluation_report.md"
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
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _csv_value(row.get(key)) for key in fieldnames})


def _git_output(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def _repo_identity() -> dict[str, str]:
    branch = _git_output("branch", "--show-current")
    local_head_sha = _git_output("rev-parse", "HEAD")
    try:
        remote_head_sha = _git_output("rev-parse", f"origin/{branch}")
    except subprocess.CalledProcessError:
        remote_head_sha = _git_output("ls-remote", "origin", f"refs/heads/{branch}").split()[0]
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


def _artifact_markdown(
    report: Feature081Report,
    *,
    output_dir: Path,
    raw_row_count: int,
    raw_rows_json_path: Path,
    raw_rows_csv_path: Path,
    aggregate_policy_json_path: Path,
    aggregate_policy_csv_path: Path,
    ranking_json_path: Path,
    ranking_csv_path: Path,
    manifest_path: Path,
) -> str:
    coverage = [
        "# Feature 081 HOODIE Evaluation & Baseline Benchmarking Artifact Bundle",
        "",
        f"- output_dir: `{output_dir}`",
        f"- raw_row_count: `{raw_row_count}`",
        f"- policies: `{len(report.policy_coverage)}`",
        f"- scenarios: `{len(report.scenario_coverage)}`",
        f"- metrics: `{len(report.metric_coverage)}`",
        f"- compatibility_mode_used: `{report.compatibility_mode_used}`",
        "",
        "## Generated Files",
        f"- `{raw_rows_json_path.name}`",
        f"- `{raw_rows_csv_path.name}`",
        f"- `{aggregate_policy_json_path.name}`",
        f"- `{aggregate_policy_csv_path.name}`",
        f"- `{ranking_json_path.name}`",
        f"- `{ranking_csv_path.name}`",
        f"- `{manifest_path.name}`",
        "",
        "## Compatibility-Mode Policies",
    ]
    compatibility_policies = [row.policy for row in report.policy_coverage if row.compatibility_mode_used]
    coverage.extend(f"- {policy}" for policy in compatibility_policies or ("none",))
    coverage.append("")
    coverage.append(render_feature_081_report(report))
    return "\n".join(coverage) + "\n"


def _execution_manifest(
    report: Feature081Report,
    *,
    config: EvaluationConfig,
    raw_row_count: int,
    raw_rows_json_path: Path,
    raw_rows_csv_path: Path,
    aggregate_policy_json_path: Path,
    aggregate_policy_csv_path: Path,
    ranking_json_path: Path,
    ranking_csv_path: Path,
    report_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    repo_identity = _repo_identity()
    compatibility_policies = [row.policy for row in report.policy_coverage if row.compatibility_mode_used]
    generated_files = [
        raw_rows_json_path.name,
        raw_rows_csv_path.name,
        aggregate_policy_json_path.name,
        aggregate_policy_csv_path.name,
        ranking_json_path.name,
        ranking_csv_path.name,
        report_path.name,
        EXECUTION_MANIFEST_JSON,
    ]
    return {
        "feature": "081",
        "feature_name": "HOODIE Evaluation & Baseline Benchmarking",
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
        "required_policies": list(REQUIRED_POLICIES),
        "required_scenarios": list(REQUIRED_SCENARIOS),
        "claim_boundary": list(report.claim_boundary),
        "scope_proof": list(report.scope_proof),
        "compatibility_mode_policies": compatibility_policies,
        "policy_coverage": [row.to_dict() for row in report.policy_coverage],
        "scenario_coverage": [row.to_dict() for row in report.scenario_coverage],
        "metric_coverage": [row.to_dict() for row in report.metric_coverage],
        "ranking_metrics": sorted(report.ranking_tables),
        "report_status": report.status,
        "passed": report.passed,
        "readiness_level": report.readiness_level,
    }


def generate_hoodie_evaluation_runner_artifacts(output_dir: Path | None = None) -> tuple[Feature081Report, dict[str, Path], dict[str, Any]]:
    config = EvaluationConfig()
    output_dir = Path(output_dir or DEFAULT_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    report = build_feature_081_report(config)
    raw_metric_rows, _, outcomes_by_key = build_execution_rows(config)
    aggregate_rows = aggregate_by_policy(raw_metric_rows)
    raw_rows = _flatten_raw_rows(outcomes_by_key)
    ranking_rows = _ranking_rows_to_dict(report.ranking_tables)

    raw_rows_json_path = output_dir / RAW_ROWS_JSON
    raw_rows_csv_path = output_dir / RAW_ROWS_CSV
    aggregate_policy_json_path = output_dir / AGGREGATE_BY_POLICY_JSON
    aggregate_policy_csv_path = output_dir / AGGREGATE_BY_POLICY_CSV
    ranking_json_path = output_dir / RANKING_BY_METRIC_JSON
    ranking_csv_path = output_dir / RANKING_BY_METRIC_CSV
    report_md_path = output_dir / REPORT_MD
    manifest_path = output_dir / EXECUTION_MANIFEST_JSON

    _dump_json(raw_rows_json_path, {"count": len(raw_rows), "rows": raw_rows})
    _write_csv(raw_rows_csv_path, raw_rows)

    aggregate_payload = {"count": len(aggregate_rows), "rows": [row.to_dict() for row in aggregate_rows]}
    _dump_json(aggregate_policy_json_path, aggregate_payload)
    _write_csv(aggregate_policy_csv_path, [row.to_dict() for row in aggregate_rows])

    _dump_json(ranking_json_path, {"metric_count": len(ranking_rows), "ranking_tables": ranking_rows})
    ranking_csv_rows: list[dict[str, Any]] = []
    for metric, rows in ranking_rows.items():
        for row in rows:
            ranking_csv_rows.append({"metric": metric, **row})
    _write_csv(ranking_csv_path, ranking_csv_rows)

    report_md_path.write_text(
        _artifact_markdown(
            report,
            output_dir=output_dir,
            raw_row_count=len(raw_rows),
            raw_rows_json_path=raw_rows_json_path,
            raw_rows_csv_path=raw_rows_csv_path,
            aggregate_policy_json_path=aggregate_policy_json_path,
            aggregate_policy_csv_path=aggregate_policy_csv_path,
            ranking_json_path=ranking_json_path,
            ranking_csv_path=ranking_csv_path,
            manifest_path=manifest_path,
        ),
        encoding="utf-8",
    )

    manifest = _execution_manifest(
        report,
        config=config,
        raw_row_count=len(raw_rows),
        raw_rows_json_path=raw_rows_json_path,
        raw_rows_csv_path=raw_rows_csv_path,
        aggregate_policy_json_path=aggregate_policy_json_path,
        aggregate_policy_csv_path=aggregate_policy_csv_path,
        ranking_json_path=ranking_json_path,
        ranking_csv_path=ranking_csv_path,
        report_path=report_md_path,
        output_dir=output_dir,
    )
    _dump_json(manifest_path, manifest)

    artifact_paths = {
        RAW_ROWS_JSON: raw_rows_json_path,
        RAW_ROWS_CSV: raw_rows_csv_path,
        AGGREGATE_BY_POLICY_JSON: aggregate_policy_json_path,
        AGGREGATE_BY_POLICY_CSV: aggregate_policy_csv_path,
        RANKING_BY_METRIC_JSON: ranking_json_path,
        RANKING_BY_METRIC_CSV: ranking_csv_path,
        REPORT_MD: report_md_path,
        EXECUTION_MANIFEST_JSON: manifest_path,
    }
    return report, artifact_paths, manifest


def generate_feature_081_evaluation_artifacts(output_dir: Path | None = None) -> tuple[Feature081Report, dict[str, Path], dict[str, Any]]:
    return generate_hoodie_evaluation_runner_artifacts(output_dir)


def write_feature_081_evaluation_artifacts(output_dir: Path | None = None) -> tuple[Feature081Report, dict[str, Path], dict[str, Any]]:
    return generate_hoodie_evaluation_runner_artifacts(output_dir)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate Feature 081 evaluation and baseline benchmarking artifacts.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Output directory for Feature 081 artifacts.")
    args = parser.parse_args(argv)
    report, _, _ = generate_hoodie_evaluation_runner_artifacts(Path(args.output_dir))
    print(render_feature_081_report(report))


if __name__ == "__main__":
    main()
