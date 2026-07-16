from __future__ import annotations

from collections import defaultdict
import csv
from dataclasses import asdict, dataclass, fields
from hashlib import sha256
import json
import math
from pathlib import Path
from typing import Any, Iterable

from .job_matrix import ProductionJobRow
from .panel_registry import PANEL_REGISTRY


@dataclass(frozen=True, slots=True)
class VerificationCheck:
    check_id: str
    passed: bool
    expected: object
    observed: object
    evidence_paths: tuple[str, ...] = ()
    failure_message: str | None = None


def _file_hash(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _load_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file() or path.stat().st_size == 0:
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _load_rows(path: Path) -> list[ProductionJobRow]:
    allowed = {field.name for field in fields(ProductionJobRow)}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"matrix must be a JSON list: {path}")
    return [
        ProductionJobRow(
            **{key: value for key, value in raw.items() if key in allowed}
        )
        for raw in payload
    ]


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _normalized(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.12g}"
    return str(value)


def _finite(value: object) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _check(
    checks: list[VerificationCheck],
    check_id: str,
    passed: bool,
    *,
    expected: object,
    observed: object,
    evidence: Iterable[Path | str] = (),
    failure: str | None = None,
) -> None:
    checks.append(
        VerificationCheck(
            check_id=check_id,
            passed=bool(passed),
            expected=expected,
            observed=observed,
            evidence_paths=tuple(str(path) for path in evidence),
            failure_message=None if passed else failure or check_id,
        )
    )


def _status_and_marker_checks(
    campaign_dir: Path,
    rows: list[ProductionJobRow],
    checks: list[VerificationCheck],
) -> set[str]:
    completed: set[str] = set()
    for row in rows:
        job_dir = campaign_dir / "jobs" / row.job_id
        status_path = job_dir / "status.json"
        marker_path = job_dir / "completion.marker"
        status: dict[str, Any] = {}
        try:
            status = _load_json(status_path)
        except (FileNotFoundError, ValueError, json.JSONDecodeError):
            pass
        is_complete = (
            status.get("status") == "completed"
            and status.get("completion_marker") is True
            and marker_path.is_file()
        )
        _check(
            checks,
            f"job.completed:{row.job_id}",
            is_complete,
            expected="completed status and completion.marker",
            observed={
                "status": status.get("status"),
                "status_marker": status.get("completion_marker"),
                "marker_exists": marker_path.exists(),
            },
            evidence=(status_path, marker_path),
            failure=f"job {row.job_id} is not scientifically complete",
        )
        if is_complete:
            completed.add(row.job_id)

        required = [status_path, job_dir / "provenance.json"]
        required.extend(
            [job_dir / "training_history.csv", job_dir / "training_metrics.csv"]
            if row.job_type == "training"
            else [
                job_dir / "evaluation_metrics.csv",
                job_dir / "task_records.csv",
                job_dir / "decision_records.csv",
            ]
        )
        existing = [path for path in required if path.is_file()]
        marker_last = bool(existing) and marker_path.is_file() and marker_path.stat().st_mtime_ns >= max(
            path.stat().st_mtime_ns for path in existing
        )
        _check(
            checks,
            f"job.completion_marker_last:{row.job_id}",
            marker_last,
            expected="completion marker timestamp not earlier than required outputs",
            observed={
                "marker_mtime_ns": marker_path.stat().st_mtime_ns
                if marker_path.exists()
                else None,
                "required_file_count": len(required),
                "existing_required_file_count": len(existing),
            },
            evidence=(*required, marker_path),
            failure=f"completion marker ordering or required output inventory failed for {row.job_id}",
        )
    return completed


def _checkpoint_registry_checks(
    campaign_dir: Path,
    rows: list[ProductionJobRow],
    checks: list[VerificationCheck],
) -> dict[str, dict[str, Any]]:
    registry_path = campaign_dir / "checkpoint_registry.json"
    try:
        registry_payload = _load_json(registry_path)
    except (FileNotFoundError, ValueError, json.JSONDecodeError):
        registry_payload = {"checkpoints": []}
    raw_records = registry_payload.get("checkpoints", [])
    records = raw_records if isinstance(raw_records, list) else []
    by_job = {
        str(record.get("training_job_id")): record
        for record in records
        if isinstance(record, dict) and record.get("training_job_id")
    }
    training_rows = [row for row in rows if row.job_type == "training"]
    _check(
        checks,
        "checkpoint_registry.exact_training_coverage",
        len(by_job) == len(training_rows)
        and set(by_job) == {row.job_id for row in training_rows},
        expected=sorted(row.job_id for row in training_rows),
        observed=sorted(by_job),
        evidence=(registry_path,),
        failure="checkpoint registry does not cover the exact training matrix",
    )

    for row in training_rows:
        record = by_job.get(row.job_id, {})
        checkpoint_path = Path(str(record.get("checkpoint_path", "")))
        exists = checkpoint_path.is_file()
        actual_hash = _file_hash(checkpoint_path) if exists else None
        expected_hash = str(record.get("checkpoint_hash", "")) or None
        exact = (
            exists
            and bool(record.get("scientifically_complete"))
            and record.get("policy") == row.policy
            and record.get("variant") == row.variant
            and int(record.get("seed", -1)) == int(row.seed or 0)
            and record.get("source_contract_hash") == row.source_contract_hash
            and expected_hash == actual_hash
        )
        _check(
            checks,
            f"checkpoint.valid:{row.job_id}",
            exact,
            expected={
                "policy": row.policy,
                "variant": row.variant,
                "seed": int(row.seed or 0),
                "source_contract_hash": row.source_contract_hash,
                "scientifically_complete": True,
                "file_hash_matches": True,
            },
            observed={
                "file_exists": exists,
                "policy": record.get("policy"),
                "variant": record.get("variant"),
                "seed": record.get("seed"),
                "source_contract_hash": record.get("source_contract_hash"),
                "scientifically_complete": record.get("scientifically_complete"),
                "expected_hash": expected_hash,
                "actual_hash": actual_hash,
            },
            evidence=(registry_path, checkpoint_path),
            failure=f"checkpoint registry or file integrity failed for {row.job_id}",
        )
        job_dir = campaign_dir / "jobs" / row.job_id
        checkpoint_dirs = [
            path
            for path in (job_dir / "internal_checkpoints").iterdir()
            if path.is_dir()
        ] if (job_dir / "internal_checkpoints").is_dir() else []
        retention_path = job_dir / "checkpoint_retention_manifest.json"
        try:
            retention = _load_json(retention_path)
        except (FileNotFoundError, ValueError, json.JSONDecodeError):
            retention = {}
        bounded = (
            len(checkpoint_dirs) <= 1
            and int(retention.get("maximum_retained_checkpoints", 0)) == 1
            and int(retention.get("replay_snapshot_count", -1)) == 0
        )
        _check(
            checks,
            f"checkpoint.retention:{row.job_id}",
            bounded,
            expected={"physical_checkpoints_max": 1, "final_replay_snapshots": 0},
            observed={
                "physical_checkpoint_count": len(checkpoint_dirs),
                "maximum_retained_checkpoints": retention.get(
                    "maximum_retained_checkpoints"
                ),
                "replay_snapshot_count": retention.get("replay_snapshot_count"),
            },
            evidence=(retention_path, job_dir / "internal_checkpoints"),
            failure=f"checkpoint retention is not bounded for {row.job_id}",
        )
    return by_job


def _training_checks(
    campaign_dir: Path,
    rows: list[ProductionJobRow],
    checks: list[VerificationCheck],
) -> None:
    for row in (item for item in rows if item.job_type == "training"):
        job_dir = campaign_dir / "jobs" / row.job_id
        history_path = job_dir / "training_history.csv"
        metrics_path = job_dir / "training_metrics.csv"
        history = _load_csv(history_path)
        metrics = _load_csv(metrics_path)
        expected = int(row.training_contract.get("training_episodes", 0))
        history_episodes = [
            int(record.get("episode_or_step", -1)) for record in history
        ]
        metric_episodes = [int(record.get("episode", -1)) for record in metrics]
        exact_range = (
            len(history) == expected
            and len(metrics) == expected
            and history_episodes == list(range(expected))
            and metric_episodes == list(range(expected))
            and len(set(history_episodes)) == expected
            and len(set(metric_episodes)) == expected
        )
        _check(
            checks,
            f"training.episode_range:{row.job_id}",
            exact_range,
            expected={"count": expected, "range": [0, max(0, expected - 1)]},
            observed={
                "history_count": len(history),
                "metrics_count": len(metrics),
                "history_first_last": history_episodes[:1] + history_episodes[-1:],
                "metrics_first_last": metric_episodes[:1] + metric_episodes[-1:],
            },
            evidence=(history_path, metrics_path),
            failure=f"training episode coverage failed for {row.job_id}",
        )
        required_metric_fields = (
            "accumulated_reward",
            "average_delay",
            "drop_ratio",
            "throughput",
            "completed_tasks",
            "dropped_tasks",
            "offered_tasks",
            "local_actions",
            "horizontal_actions",
            "vertical_actions",
            "mean_loss",
            "epsilon",
        )
        metric_issues: list[str] = []
        for index, record in enumerate(metrics):
            for field in required_metric_fields:
                if not _finite(record.get(field)):
                    metric_issues.append(f"row={index}:{field}:not_finite")
            try:
                completed = int(record.get("completed_tasks", -1))
                dropped = int(record.get("dropped_tasks", -1))
                offered = int(record.get("offered_tasks", -1))
                drop_ratio = float(record.get("drop_ratio", "nan"))
                actions = sum(
                    int(record.get(field, -1))
                    for field in (
                        "local_actions",
                        "horizontal_actions",
                        "vertical_actions",
                    )
                )
                if completed + dropped != offered:
                    metric_issues.append(f"row={index}:terminal_accounting")
                if actions != offered:
                    metric_issues.append(f"row={index}:action_accounting")
                expected_ratio = dropped / offered if offered else 0.0
                if not math.isclose(drop_ratio, expected_ratio, rel_tol=1e-9, abs_tol=1e-12):
                    metric_issues.append(f"row={index}:drop_ratio_denominator")
            except (TypeError, ValueError):
                metric_issues.append(f"row={index}:invalid_integer_metric")
        _check(
            checks,
            f"training.metrics:{row.job_id}",
            not metric_issues,
            expected="finite panel metrics and exact task/action denominators",
            observed=metric_issues[:50],
            evidence=(metrics_path,),
            failure=f"training scientific metrics failed for {row.job_id}",
        )


def _evaluation_checks(
    campaign_dir: Path,
    rows: list[ProductionJobRow],
    checkpoints: dict[str, dict[str, Any]],
    checks: list[VerificationCheck],
) -> dict[str, tuple[tuple[object, ...], ...]]:
    trace_signatures: dict[str, tuple[tuple[object, ...], ...]] = {}
    for row in (item for item in rows if item.job_type == "evaluation"):
        job_dir = campaign_dir / "jobs" / row.job_id
        status_path = job_dir / "status.json"
        metrics_path = job_dir / "evaluation_metrics.csv"
        task_path = job_dir / "task_records.csv"
        decision_path = job_dir / "decision_records.csv"
        status = _load_json(status_path) if status_path.is_file() else {}
        metrics = _load_csv(metrics_path)
        tasks = _load_csv(task_path)
        decisions = _load_csv(decision_path)
        expected_episodes = int(row.evaluation_contract.get("validation_episodes", 0))
        episode_ids = [int(record.get("episode", -1)) for record in metrics]
        exact_episodes = (
            len(metrics) == expected_episodes
            and episode_ids == list(range(expected_episodes))
            and len(set(episode_ids)) == expected_episodes
        )
        _check(
            checks,
            f"evaluation.episode_range:{row.job_id}",
            exact_episodes,
            expected={
                "count": expected_episodes,
                "range": [0, max(0, expected_episodes - 1)],
            },
            observed={
                "count": len(metrics),
                "first_last": episode_ids[:1] + episode_ids[-1:],
            },
            evidence=(metrics_path,),
            failure=f"evaluation episode coverage failed for {row.job_id}",
        )

        metric_issues: list[str] = []
        total_tasks = 0
        signature: list[tuple[object, ...]] = []
        for index, record in enumerate(metrics):
            for field in (
                "average_reward",
                "average_delay",
                "drop_ratio",
                "throughput",
                "completed_tasks",
                "dropped_tasks",
                "total_tasks",
                "local_actions",
                "horizontal_actions",
                "vertical_actions",
            ):
                if not _finite(record.get(field)):
                    metric_issues.append(f"row={index}:{field}:not_finite")
            try:
                completed = int(record.get("completed_tasks", -1))
                dropped = int(record.get("dropped_tasks", -1))
                total = int(record.get("total_tasks", -1))
                drop_ratio = float(record.get("drop_ratio", "nan"))
                actions = sum(
                    int(record.get(field, -1))
                    for field in (
                        "local_actions",
                        "horizontal_actions",
                        "vertical_actions",
                    )
                )
                if completed + dropped != total:
                    metric_issues.append(f"row={index}:terminal_accounting")
                if actions != total:
                    metric_issues.append(f"row={index}:action_accounting")
                expected_ratio = dropped / total if total else 0.0
                if not math.isclose(drop_ratio, expected_ratio, rel_tol=1e-9, abs_tol=1e-12):
                    metric_issues.append(f"row={index}:drop_ratio_denominator")
                total_tasks += total
                signature.append((record.get("trace_id"), total))
            except (TypeError, ValueError):
                metric_issues.append(f"row={index}:invalid_integer_metric")
        _check(
            checks,
            f"evaluation.metrics:{row.job_id}",
            not metric_issues,
            expected="finite metrics and exact task/action denominators",
            observed=metric_issues[:50],
            evidence=(metrics_path,),
            failure=f"evaluation scientific metrics failed for {row.job_id}",
        )

        task_keys = [
            (record.get("run_id"), record.get("task_id")) for record in tasks
        ]
        observation_refs = [record.get("observation_ref") for record in decisions]
        records_valid = (
            len(tasks) == total_tasks
            and len(task_keys) == len(set(task_keys))
            and len(decisions) == total_tasks
            and len(observation_refs) == len(set(observation_refs))
            and all(reference not in {None, ""} for reference in observation_refs)
        )
        _check(
            checks,
            f"evaluation.record_inventory:{row.job_id}",
            records_valid,
            expected={
                "task_records": total_tasks,
                "decision_records": total_tasks,
                "unique_task_keys": True,
                "unique_observation_refs": True,
            },
            observed={
                "task_records": len(tasks),
                "decision_records": len(decisions),
                "unique_task_keys": len(set(task_keys)),
                "unique_observation_refs": len(set(observation_refs)),
            },
            evidence=(task_path, decision_path, metrics_path),
            failure=f"evaluation record inventory failed for {row.job_id}",
        )

        if row.policy == "HOODIE":
            dependency = row.checkpoint_dependency
            record = checkpoints.get(str(dependency)) if dependency else None
            expected_hash = str((record or {}).get("checkpoint_hash", ""))
            exact_dependency = (
                bool(dependency)
                and record is not None
                and bool(record.get("scientifically_complete"))
                and str(status.get("checkpoint_hash", "")) == expected_hash
            )
        else:
            dependency = row.checkpoint_dependency
            expected_hash = "baseline-no-checkpoint"
            exact_dependency = (
                dependency is None
                and str(status.get("checkpoint_hash", "baseline-no-checkpoint"))
                in {"", "baseline-no-checkpoint"}
            )
        _check(
            checks,
            f"evaluation.checkpoint_dependency:{row.job_id}",
            exact_dependency,
            expected={
                "dependency": dependency if row.policy == "HOODIE" else None,
                "checkpoint_hash": expected_hash,
            },
            observed={
                "dependency": row.checkpoint_dependency,
                "status_checkpoint_hash": status.get("checkpoint_hash"),
            },
            evidence=(status_path, campaign_dir / "checkpoint_registry.json"),
            failure=f"exact checkpoint dependency failed for {row.job_id}",
        )

        task_signature = tuple(
            sorted(
                (
                    record.get("run_id"),
                    record.get("task_id"),
                    record.get("source_agent"),
                    record.get("arrival_slot"),
                    record.get("deadline"),
                    record.get("workload"),
                )
                for record in tasks
            )
        )
        trace_signatures[row.job_id] = tuple(signature) + task_signature
    return trace_signatures


def _fairness_checks(
    rows: list[ProductionJobRow],
    signatures: dict[str, tuple[tuple[object, ...], ...]],
    checks: list[VerificationCheck],
) -> None:
    groups: dict[tuple[object, ...], list[ProductionJobRow]] = defaultdict(list)
    for row in rows:
        if row.job_type != "evaluation":
            continue
        counts = row.topology_contract.get("agent_counts", [20])
        agent_count = int(counts[0] if isinstance(counts, (list, tuple)) else counts)
        key = (
            row.panel_id,
            row.trace_bank_id,
            _normalized(row.independent_value),
            int(row.seed or 0),
            agent_count,
        )
        groups[key].append(row)
    for key, group in groups.items():
        if len(group) < 2:
            continue
        observed = {
            row.job_id: sha256(_canonical(signatures.get(row.job_id, ())).encode()).hexdigest()
            for row in group
        }
        _check(
            checks,
            f"fairness.paired_trace:{sha256(_canonical(key).encode()).hexdigest()[:16]}",
            len(set(observed.values())) == 1,
            expected="identical task and trace signatures across compared policies",
            observed=observed,
            evidence=tuple(row.job_id for row in group),
            failure=f"paired trace mismatch for group {key}",
        )


def _aggregate_checks(
    campaign_dir: Path,
    rows: list[ProductionJobRow],
    completed: set[str],
    checks: list[VerificationCheck],
) -> None:
    from .scientific_pipeline import REQUIRED_PANELS

    manifest_path = campaign_dir / "aggregation_manifest.json"
    try:
        manifest = _load_json(manifest_path)
    except (FileNotFoundError, ValueError, json.JSONDecodeError):
        manifest = {"datasets": {}}
    datasets = manifest.get("datasets", {})
    _check(
        checks,
        "aggregate.panel_manifest_coverage",
        set(datasets) == set(REQUIRED_PANELS),
        expected=sorted(REQUIRED_PANELS),
        observed=sorted(datasets) if isinstance(datasets, dict) else [],
        evidence=(manifest_path,),
        failure="aggregation manifest does not contain exactly 14 required panels",
    )

    for panel_id in REQUIRED_PANELS:
        entry = datasets.get(panel_id, {}) if isinstance(datasets, dict) else {}
        path = Path(str(entry.get("path", "")))
        aggregate_rows = _load_csv(path)
        actual_hash = _file_hash(path) if path.is_file() else None
        manifest_hash = entry.get("hash")
        values_finite = bool(aggregate_rows)
        issues: list[str] = []
        for index, record in enumerate(aggregate_rows):
            for field in (
                "sample_count",
                "mean",
                "standard_deviation",
                "confidence_interval_low",
                "confidence_interval_high",
            ):
                if not _finite(record.get(field)):
                    issues.append(f"row={index}:{field}:not_finite")
            if _finite(record.get("confidence_interval_low")) and _finite(
                record.get("confidence_interval_high")
            ) and float(record["confidence_interval_low"]) > float(
                record["confidence_interval_high"]
            ):
                issues.append(f"row={index}:confidence_interval_order")
        values_finite = values_finite and not issues
        panel_jobs = [row for row in rows if row.panel_id == panel_id]
        if panel_id in {"figure_8a", "figure_8b"}:
            panel_jobs = [
                row
                for row in panel_jobs
                if not bool(row.training_contract.get("reference_only", False))
            ]
        expected_contributors = {row.job_id for row in panel_jobs}
        manifest_contributors = set(entry.get("contributing_job_ids", []))
        row_contributors = {
            job_id
            for record in aggregate_rows
            for job_id in str(record.get("contributing_job_ids", "")).split(",")
            if job_id
        }
        contributors_valid = (
            manifest_contributors == expected_contributors
            and row_contributors <= expected_contributors
            and expected_contributors <= completed
        )
        if panel_id in {"figure_8a", "figure_8b", "figure_11"}:
            expected_x = {
                _normalized(value)
                for value in PANEL_REGISTRY[panel_id].source_contract.get(
                    "training_episode_points", []
                )
            }
        else:
            expected_x = {_normalized(row.independent_value) for row in panel_jobs}
        observed_x = {_normalized(record.get("x_value")) for record in aggregate_rows}
        x_valid = observed_x == expected_x and len(observed_x) >= 2
        if panel_id == "figure_9b":
            expected_series = {
                f"{row.series_name} / {category}"
                for row in panel_jobs
                for category in ("Local", "Horizontal", "Vertical")
            }
        else:
            expected_series = {
                str(row.series_name or row.variant or row.policy) for row in panel_jobs
            }
        observed_series = {str(record.get("series")) for record in aggregate_rows}
        series_valid = observed_series == expected_series
        panel_valid = (
            path.is_file()
            and actual_hash == manifest_hash
            and values_finite
            and contributors_valid
            and x_valid
            and series_valid
        )
        _check(
            checks,
            f"aggregate.panel:{panel_id}",
            panel_valid,
            expected={
                "file_hash_matches": True,
                "finite_nonempty": True,
                "contributors": sorted(expected_contributors),
                "x_values": sorted(expected_x),
                "series": sorted(expected_series),
            },
            observed={
                "path": str(path),
                "file_exists": path.exists(),
                "manifest_hash": manifest_hash,
                "actual_hash": actual_hash,
                "rows": len(aggregate_rows),
                "issues": issues[:50],
                "contributors": sorted(manifest_contributors),
                "x_values": sorted(observed_x),
                "series": sorted(observed_series),
            },
            evidence=(manifest_path, path),
            failure=f"aggregate scientific contract failed for {panel_id}",
        )


def _render_lineage_checks(
    campaign_dir: Path, checks: list[VerificationCheck]
) -> bool:
    manifest_path = campaign_dir / "figures" / "render_manifest.json"
    if not manifest_path.is_file():
        return False
    manifest = _load_json(manifest_path)
    figures = manifest.get("figures", {})
    from .scientific_pipeline import COMPOSITES, REQUIRED_PANELS

    expected = set(REQUIRED_PANELS) | set(COMPOSITES)
    inventory_valid = set(figures) == expected
    issues: list[str] = []
    for figure_id, entry in figures.items():
        if figure_id in REQUIRED_PANELS:
            aggregate_path = Path(str(entry.get("aggregate_input_path", "")))
            if not aggregate_path.is_file() or _file_hash(aggregate_path) != entry.get(
                "aggregate_input_hash"
            ):
                issues.append(f"{figure_id}:aggregate_lineage")
        outputs = entry.get("outputs", {})
        hashes = entry.get("output_hashes", {})
        if set(outputs) != {"png", "svg", "pdf"}:
            issues.append(f"{figure_id}:format_inventory")
        for extension, raw_path in outputs.items():
            path = Path(str(raw_path))
            if not path.is_file() or _file_hash(path) != hashes.get(extension):
                issues.append(f"{figure_id}:{extension}:hash")
    _check(
        checks,
        "render.lineage",
        inventory_valid and not issues,
        expected={"figures": sorted(expected), "formats": ["pdf", "png", "svg"]},
        observed={"figures": sorted(figures), "issues": issues},
        evidence=(manifest_path,),
        failure="rendered output lineage failed",
    )
    return True


def verify_campaign(
    campaign_id: str, matrix_path: Path | None = None
) -> dict[str, Any]:
    from . import scientific_pipeline as pipeline

    campaign_dir = pipeline.CAMPAIGN_ROOT / campaign_id
    rows = (
        _load_rows(matrix_path)
        if matrix_path is not None
        else _load_rows(campaign_dir / "job_plan.json")
    )
    checks: list[VerificationCheck] = []
    job_ids = [row.job_id for row in rows]
    _check(
        checks,
        "matrix.unique_job_ids",
        len(job_ids) == len(set(job_ids)),
        expected=len(job_ids),
        observed=len(set(job_ids)),
        evidence=(matrix_path or campaign_dir / "job_plan.json",),
        failure="matrix contains duplicate job IDs",
    )
    completed = _status_and_marker_checks(campaign_dir, rows, checks)
    checkpoints = _checkpoint_registry_checks(campaign_dir, rows, checks)
    _training_checks(campaign_dir, rows, checks)
    signatures = _evaluation_checks(campaign_dir, rows, checkpoints, checks)
    _fairness_checks(rows, signatures, checks)
    _aggregate_checks(campaign_dir, rows, completed, checks)
    render_checked = _render_lineage_checks(campaign_dir, checks)

    required_checks = [check for check in checks if check.check_id != "render.lineage"]
    passed = bool(required_checks) and all(check.passed for check in required_checks)
    if render_checked:
        passed = passed and all(
            check.passed for check in checks if check.check_id == "render.lineage"
        )

    details = [asdict(check) for check in checks]
    integrity_passed = all(
        check.passed
        for check in checks
        if check.check_id.startswith(
            ("matrix.", "job.", "training.", "evaluation.", "checkpoint.")
        )
    )
    fairness_passed = all(
        check.passed for check in checks if check.check_id.startswith("fairness.")
    )
    sanity_passed = all(
        check.passed
        for check in checks
        if check.check_id.startswith(("training.metrics", "evaluation.metrics"))
    )
    lineage_passed = all(
        check.passed
        for check in checks
        if check.check_id.startswith(("aggregate.", "render."))
    )
    payload = {
        "campaign_id": campaign_id,
        "verified": passed,
        "check_count": len(checks),
        "passed_check_count": sum(check.passed for check in checks),
        "failed_check_count": sum(not check.passed for check in checks),
        "all_required_checks_passed": integrity_passed,
        "all_fairness_checks_passed": fairness_passed,
        "all_scientific_sanity_checks_passed": sanity_passed,
        "all_render_lineage_checks_passed": lineage_passed,
        "render_outputs_checked": render_checked,
        "checks": details,
    }
    pipeline._write_json(campaign_dir / "verification_report.json", payload)
    pipeline._write_json(
        campaign_dir / "fairness_report.json",
        {
            "campaign_id": campaign_id,
            "all_fairness_checks_passed": fairness_passed,
            "checks": [
                asdict(check)
                for check in checks
                if check.check_id.startswith("fairness.")
            ],
        },
    )
    pipeline._write_json(
        campaign_dir / "scientific_sanity_report.json",
        {
            "campaign_id": campaign_id,
            "all_scientific_sanity_checks_passed": sanity_passed,
            "checks": [
                asdict(check)
                for check in checks
                if check.check_id.startswith(("training.metrics", "evaluation.metrics"))
            ],
        },
    )
    pipeline._write_json(
        campaign_dir / "lineage_report.json",
        {
            "campaign_id": campaign_id,
            "all_render_lineage_checks_passed": lineage_passed,
            "render_outputs_checked": render_checked,
            "checks": [
                asdict(check)
                for check in checks
                if check.check_id.startswith(("aggregate.", "render."))
            ],
        },
    )
    pipeline._write_json(campaign_dir / "final_verification.json", payload)
    if not passed:
        failures = [
            check.check_id for check in checks if not check.passed
        ]
        raise ValueError(
            "campaign verification failed: " + ", ".join(failures[:25])
        )
    return payload


def install_verification_patch() -> None:
    from . import distributed_v2, scientific_pipeline

    scientific_pipeline.verify_campaign = verify_campaign
    distributed_v2.verify_campaign = verify_campaign
