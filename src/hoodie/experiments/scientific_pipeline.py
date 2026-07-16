from __future__ import annotations

from dataclasses import asdict, fields, replace
from hashlib import sha256
import csv
import json
import math
from pathlib import Path
import shutil
import tempfile
from statistics import mean, pstdev
from typing import Any, Iterable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .job_matrix import ProductionJobRow
from .matrix_patch import install_matrix_patch
from .panel_registry import PANEL_REGISTRY
from .production_campaign import _load_csv_rows

CAMPAIGN_ROOT = Path("artifacts/hoodie/campaigns")
RELEASE_ROOT = Path("artifacts/hoodie/releases")
REQUIRED_PANELS = (
    "figure_8a",
    "figure_8b",
    "figure_9a",
    "figure_9b",
    "figure_9c",
    "figure_9d",
    "figure_9e",
    "figure_10a",
    "figure_10b",
    "figure_10c",
    "figure_10d",
    "figure_10e",
    "figure_10f",
    "figure_11",
)
COMPOSITES = {
    "figure_8": ("figure_8a", "figure_8b"),
    "figure_9": ("figure_9a", "figure_9b", "figure_9c", "figure_9d", "figure_9e"),
    "figure_10": (
        "figure_10a",
        "figure_10b",
        "figure_10c",
        "figure_10d",
        "figure_10e",
        "figure_10f",
    ),
    "figure_11": ("figure_11",),
}


def _canonical(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _hash(payload: object) -> str:
    return sha256(_canonical(payload).encode("utf-8")).hexdigest()


def _file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, payload: object) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return _hash(payload)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"refusing to write empty scientific dataset: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return _file_hash(path)


def _load_matrix(path: Path) -> list[ProductionJobRow]:
    allowed = {field.name for field in fields(ProductionJobRow)}
    return [
        ProductionJobRow(**{key: value for key, value in raw.items() if key in allowed})
        for raw in json.loads(path.read_text(encoding="utf-8"))
    ]


def _campaign_rows(campaign_dir: Path) -> list[ProductionJobRow]:
    plan = campaign_dir / "job_plan.json"
    if not plan.exists():
        raise FileNotFoundError(f"campaign job plan is missing: {plan}")
    rows = _load_matrix(plan)
    if len(rows) != len({row.job_id for row in rows}):
        raise ValueError("campaign job plan contains duplicate job IDs")
    return rows


def _completed_job_dir(campaign_dir: Path, row: ProductionJobRow) -> Path:
    job_dir = campaign_dir / "jobs" / row.job_id
    status_path = job_dir / "status.json"
    marker = job_dir / "completion.marker"
    if not status_path.exists() or not marker.exists():
        raise FileNotFoundError(f"job is not complete: {row.job_id}")
    status = json.loads(status_path.read_text(encoding="utf-8"))
    if status.get("status") != "completed":
        raise ValueError(f"job status is not completed: {row.job_id}")
    return job_dir


def _ci95(values: list[float]) -> tuple[float, float, float, float]:
    if not values:
        raise ValueError("cannot aggregate an empty value list")
    value_mean = mean(values)
    std = pstdev(values) if len(values) > 1 else 0.0
    half_width = 1.96 * std / math.sqrt(len(values)) if len(values) > 1 else 0.0
    return value_mean, std, value_mean - half_width, value_mean + half_width


def _sample_episode(rows: list[dict[str, Any]], x_value: int, *, total: int) -> dict[str, Any]:
    if not rows:
        raise ValueError("training metrics are empty")
    # Curve labels use completed-episode counts. Episode zero is the first observed
    # point; a label equal to the total maps to the final zero-based episode.
    target = 0 if x_value == 0 else min(total - 1, x_value - 1)
    indexed = {int(row["episode"]): row for row in rows}
    if target in indexed:
        return indexed[target]
    eligible = [episode for episode in indexed if episode <= target]
    if not eligible:
        raise ValueError(f"no training metric available at or before episode {target}")
    return indexed[max(eligible)]


def _training_panel_rows(campaign_dir: Path, panel_id: str, jobs: list[ProductionJobRow]) -> list[dict[str, Any]]:
    contract = PANEL_REGISTRY[panel_id].source_contract
    output: list[dict[str, Any]] = []
    if panel_id in {"figure_8a", "figure_8b"}:
        jobs = [job for job in jobs if not bool(job.training_contract.get("reference_only", False))]
        x_points = [int(value) for value in contract["training_episode_points"]]
        y_field = "accumulated_reward"
    elif panel_id == "figure_11":
        x_points = [int(value) for value in contract["training_episode_points"]]
        y_field = "average_delay"
    else:
        raise ValueError(f"unsupported training panel: {panel_id}")
    for job in jobs:
        job_dir = _completed_job_dir(campaign_dir, job)
        metrics_path = job_dir / "training_metrics.csv"
        metrics = _load_csv_rows(metrics_path)
        total = int(job.training_contract["training_episodes"])
        for x_value in x_points:
            sampled = _sample_episode(metrics, x_value, total=total)
            value = float(sampled[y_field])
            output.append(
                {
                    "panel_id": panel_id,
                    "x_variable": "training_episode",
                    "x_value": x_value,
                    "series": job.series_name or job.variant or job.job_id,
                    "policy": job.policy,
                    "variant": job.variant,
                    "dependent_metric": y_field,
                    "sample_count": 1,
                    "mean": value,
                    "standard_deviation": 0.0,
                    "confidence_interval_low": value,
                    "confidence_interval_high": value,
                    "contributing_job_ids": job.job_id,
                    "source_dataset_hashes": _file_hash(metrics_path),
                }
            )
    return output


def _evaluation_metric_values(metrics: list[dict[str, Any]], field: str) -> list[float]:
    values = [float(row[field]) for row in metrics]
    if not values or any(not math.isfinite(value) for value in values):
        raise ValueError(f"invalid or empty evaluation metric: {field}")
    return values


def _evaluation_panel_rows(campaign_dir: Path, panel_id: str, jobs: list[ProductionJobRow]) -> list[dict[str, Any]]:
    contract = PANEL_REGISTRY[panel_id].source_contract
    dependent = str(contract["dependent_metric"])
    output: list[dict[str, Any]] = []
    for job in jobs:
        job_dir = _completed_job_dir(campaign_dir, job)
        metrics_path = job_dir / "evaluation_metrics.csv"
        metrics = _load_csv_rows(metrics_path)
        if panel_id == "figure_9b":
            categories = (
                ("Local", "local_actions"),
                ("Horizontal", "horizontal_actions"),
                ("Vertical", "vertical_actions"),
            )
            for label, field in categories:
                values = _evaluation_metric_values(metrics, field)
                value_mean, std, low, high = _ci95(values)
                output.append(
                    {
                        "panel_id": panel_id,
                        "x_variable": job.independent_variable,
                        "x_value": job.independent_value,
                        "series": f"{job.series_name} / {label}",
                        "policy": job.policy,
                        "variant": job.variant,
                        "dependent_metric": "action_count",
                        "sample_count": len(values),
                        "mean": value_mean,
                        "standard_deviation": std,
                        "confidence_interval_low": low,
                        "confidence_interval_high": high,
                        "contributing_job_ids": job.job_id,
                        "source_dataset_hashes": _file_hash(metrics_path),
                    }
                )
            continue
        field_map = {
            "average_reward": "average_reward",
            "average_delay": "average_delay",
            "task_drop_ratio": "drop_ratio",
            "drop_ratio": "drop_ratio",
            "throughput": "throughput",
        }
        if dependent not in field_map:
            raise ValueError(f"unsupported dependent metric {dependent!r} for {panel_id}")
        field = field_map[dependent]
        values = _evaluation_metric_values(metrics, field)
        value_mean, std, low, high = _ci95(values)
        output.append(
            {
                "panel_id": panel_id,
                "x_variable": job.independent_variable,
                "x_value": job.independent_value,
                "series": job.series_name or job.policy,
                "policy": job.policy,
                "variant": job.variant,
                "dependent_metric": dependent,
                "sample_count": len(values),
                "mean": value_mean,
                "standard_deviation": std,
                "confidence_interval_low": low,
                "confidence_interval_high": high,
                "contributing_job_ids": job.job_id,
                "source_dataset_hashes": _file_hash(metrics_path),
            }
        )
    return output


def build_pilot_matrix(output: Path) -> dict[str, Any]:
    """Build a clearly isolated tiny integration matrix, never a paper result."""
    from .distributed import build_integration_campaign

    integration = build_integration_campaign(output.parent, seed=7)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(integration.matrix_path.read_text(encoding="utf-8"), encoding="utf-8")
    return {
        "campaign_id": integration.campaign_id,
        "output": str(output),
        "row_count": len(integration.rows),
        "result_label": "INTEGRATION ONLY — NOT PAPER-SCALE RESULT",
    }


def aggregate_campaign(campaign_id: str) -> dict[str, Any]:
    campaign_dir = CAMPAIGN_ROOT / campaign_id
    rows = _campaign_rows(campaign_dir)
    out_dir = campaign_dir / "aggregates"
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {
        "campaign_id": campaign_id,
        "aggregation_version": 2,
        "matrix_hash": _hash([asdict(row) for row in rows]),
        "datasets": {},
        "contributing_jobs": [],
    }
    datasets: dict[str, str] = {}
    for panel_id in REQUIRED_PANELS:
        jobs = [row for row in rows if row.panel_id == panel_id]
        if not jobs:
            raise FileNotFoundError(f"job plan has no rows for {panel_id}")
        dataset_rows = (
            _training_panel_rows(campaign_dir, panel_id, jobs)
            if panel_id in {"figure_8a", "figure_8b", "figure_11"}
            else _evaluation_panel_rows(campaign_dir, panel_id, jobs)
        )
        dataset_path = out_dir / f"{panel_id}.csv"
        dataset_hash = _write_csv(dataset_path, dataset_rows)
        contributing = sorted({row["contributing_job_ids"] for row in dataset_rows})
        manifest["contributing_jobs"].extend(contributing)
        manifest["datasets"][panel_id] = {
            "path": str(dataset_path),
            "hash": dataset_hash,
            "rows": len(dataset_rows),
            "dependent_metric": str(PANEL_REGISTRY[panel_id].source_contract["dependent_metric"]),
            "contributing_job_ids": contributing,
        }
        datasets[panel_id] = str(dataset_path)
    manifest["contributing_jobs"] = sorted(set(manifest["contributing_jobs"]))
    manifest_path = campaign_dir / "aggregation_manifest.json"
    _write_json(manifest_path, manifest)
    return {
        "campaign_id": campaign_id,
        "aggregation_manifest": str(manifest_path),
        "datasets": datasets,
    }


def _finite_dataset(path: Path) -> tuple[bool, list[str]]:
    issues: list[str] = []
    rows = _load_csv_rows(path)
    if not rows:
        return False, ["empty_dataset"]
    for index, row in enumerate(rows):
        for field in (
            "mean",
            "standard_deviation",
            "confidence_interval_low",
            "confidence_interval_high",
        ):
            try:
                value = float(row[field])
            except (KeyError, TypeError, ValueError):
                issues.append(f"row_{index}:{field}:not_numeric")
                continue
            if not math.isfinite(value):
                issues.append(f"row_{index}:{field}:not_finite")
        if float(row.get("confidence_interval_low", 0)) > float(row.get("confidence_interval_high", 0)):
            issues.append(f"row_{index}:invalid_confidence_interval")
    return not issues, issues


def _fairness_checks(campaign_dir: Path, rows: list[ProductionJobRow]) -> dict[str, Any]:
    issues: list[str] = []
    groups: dict[tuple[str, str, str, int], list[ProductionJobRow]] = {}
    for row in rows:
        if not row.panel_id.startswith("figure_10") or row.job_type != "evaluation":
            continue
        key = (
            row.panel_id,
            row.independent_variable,
            str(row.independent_value),
            int(row.seed or 0),
        )
        groups.setdefault(key, []).append(row)
    checked_groups = 0
    for key, group in groups.items():
        if len(group) <= 1:
            continue
        signatures: set[tuple[tuple[str, int], ...]] = set()
        for row in group:
            metrics = _load_csv_rows(_completed_job_dir(campaign_dir, row) / "evaluation_metrics.csv")
            signatures.add(
                tuple((str(record["trace_id"]), int(record["total_tasks"])) for record in metrics)
            )
        checked_groups += 1
        if len(signatures) != 1:
            issues.append(f"paired_trace_mismatch:{key}")
    return {
        "all_fairness_checks_passed": not issues,
        "checked_groups": checked_groups,
        "issues": issues,
    }


def _job_integrity_checks(campaign_dir: Path, rows: list[ProductionJobRow]) -> dict[str, Any]:
    issues: list[str] = []
    registry_path = campaign_dir / "checkpoint_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8")) if registry_path.exists() else {"checkpoints": []}
    checkpoints = {item.get("training_job_id"): item for item in registry.get("checkpoints", [])}
    for row in rows:
        try:
            job_dir = _completed_job_dir(campaign_dir, row)
        except (FileNotFoundError, ValueError) as exc:
            issues.append(str(exc))
            continue
        provenance = job_dir / "provenance.json"
        if not provenance.exists():
            issues.append(f"missing_provenance:{row.job_id}")
        if row.job_type == "training":
            history = _load_csv_rows(job_dir / "training_history.csv")
            expected = int(row.training_contract["training_episodes"])
            episodes = [int(item["episode_or_step"]) for item in history]
            if episodes != list(range(expected)):
                issues.append(f"training_episode_range:{row.job_id}")
            metrics = _load_csv_rows(job_dir / "training_metrics.csv")
            if len(metrics) != expected:
                issues.append(f"training_metric_count:{row.job_id}")
            if row.job_id not in checkpoints:
                issues.append(f"unregistered_checkpoint:{row.job_id}")
        elif row.checkpoint_dependency:
            checkpoint = checkpoints.get(row.checkpoint_dependency)
            if checkpoint is None:
                issues.append(f"missing_dependency:{row.job_id}:{row.checkpoint_dependency}")
            elif not Path(str(checkpoint.get("checkpoint_path", ""))).exists():
                issues.append(f"missing_checkpoint_file:{row.checkpoint_dependency}")
            metrics = _load_csv_rows(job_dir / "evaluation_metrics.csv")
            expected = int(row.evaluation_contract["validation_episodes"])
            if len(metrics) != expected:
                issues.append(f"evaluation_episode_count:{row.job_id}")
    return {
        "all_required_checks_passed": not issues,
        "checked_jobs": len(rows),
        "issues": issues,
    }


def _scientific_sanity_checks(campaign_dir: Path, rows: list[ProductionJobRow]) -> dict[str, Any]:
    issues: list[str] = []
    for row in rows:
        job_dir = campaign_dir / "jobs" / row.job_id
        if row.job_type == "training" and (job_dir / "training_metrics.csv").exists():
            metrics = _load_csv_rows(job_dir / "training_metrics.csv")
            epsilons = [float(item["epsilon"]) for item in metrics]
            if any(not 0.0 <= value <= 1.0 for value in epsilons):
                issues.append(f"epsilon_range:{row.job_id}")
            if any(right > left + 1e-12 for left, right in zip(epsilons, epsilons[1:])):
                issues.append(f"epsilon_not_monotonic:{row.job_id}")
            midpoint = len(epsilons) // 2
            if any(abs(value) > 1e-12 for value in epsilons[midpoint:]):
                issues.append(f"epsilon_not_zero_after_midpoint:{row.job_id}")
        if row.job_type == "evaluation" and (job_dir / "evaluation_metrics.csv").exists():
            for metric in _load_csv_rows(job_dir / "evaluation_metrics.csv"):
                drop = float(metric["drop_ratio"])
                if not 0.0 <= drop <= 1.0:
                    issues.append(f"drop_ratio_range:{row.job_id}")
                if int(metric["completed_tasks"]) + int(metric["dropped_tasks"]) != int(metric["total_tasks"]):
                    issues.append(f"task_accounting:{row.job_id}")
    return {
        "all_scientific_sanity_checks_passed": not issues,
        "issues": issues,
    }


def verify_campaign(campaign_id: str, matrix_path: Path | None = None) -> dict[str, Any]:
    campaign_dir = CAMPAIGN_ROOT / campaign_id
    rows = _load_matrix(matrix_path) if matrix_path is not None else _campaign_rows(campaign_dir)
    aggregation_path = campaign_dir / "aggregation_manifest.json"
    if not aggregation_path.exists():
        aggregate_campaign(campaign_id)
    aggregation = json.loads(aggregation_path.read_text(encoding="utf-8"))
    integrity = _job_integrity_checks(campaign_dir, rows)
    fairness = _fairness_checks(campaign_dir, rows)
    sanity = _scientific_sanity_checks(campaign_dir, rows)
    lineage_issues: list[str] = []
    completed_ids = {row.job_id for row in rows if (campaign_dir / "jobs" / row.job_id / "completion.marker").exists()}
    for panel_id in REQUIRED_PANELS:
        dataset = aggregation.get("datasets", {}).get(panel_id)
        if not dataset:
            lineage_issues.append(f"missing_dataset_manifest:{panel_id}")
            continue
        path = Path(dataset["path"])
        if not path.exists() or _file_hash(path) != dataset["hash"]:
            lineage_issues.append(f"dataset_hash_mismatch:{panel_id}")
        valid, issues = _finite_dataset(path)
        if not valid:
            lineage_issues.extend(f"{panel_id}:{issue}" for issue in issues)
        for job_id in dataset.get("contributing_job_ids", []):
            if job_id not in completed_ids:
                lineage_issues.append(f"noncompleted_contributor:{panel_id}:{job_id}")
    lineage = {
        "all_render_lineage_checks_passed": not lineage_issues,
        "issues": lineage_issues,
    }
    _write_json(campaign_dir / "verification_report.json", {"campaign_id": campaign_id, **integrity})
    _write_json(campaign_dir / "fairness_report.json", {"campaign_id": campaign_id, **fairness})
    _write_json(campaign_dir / "scientific_sanity_report.json", {"campaign_id": campaign_id, **sanity})
    _write_json(campaign_dir / "lineage_report.json", {"campaign_id": campaign_id, **lineage})
    passed = all(
        (
            integrity["all_required_checks_passed"],
            fairness["all_fairness_checks_passed"],
            sanity["all_scientific_sanity_checks_passed"],
            lineage["all_render_lineage_checks_passed"],
        )
    )
    final = {
        "campaign_id": campaign_id,
        "verified": passed,
        **integrity,
        **fairness,
        **sanity,
        **lineage,
    }
    _write_json(campaign_dir / "final_verification.json", final)
    if not passed:
        raise ValueError("campaign verification failed; inspect verification reports")
    return final


def _load_panel_csv(path: Path) -> list[dict[str, Any]]:
    return _load_csv_rows(path)


def _numeric_x(rows: list[dict[str, Any]]) -> tuple[list[float], list[str] | None]:
    labels: list[str] = []
    values: list[float] = []
    numeric = True
    for index, row in enumerate(rows):
        raw = row["x_value"]
        try:
            values.append(float(raw))
        except (TypeError, ValueError):
            numeric = False
            values.append(float(index))
            labels.append(str(raw))
    return values, None if numeric else labels


def _plot_panel(ax: plt.Axes, rows: list[dict[str, Any]], title: str) -> None:
    series_map: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        series_map.setdefault(str(row["series"]), []).append(row)
    for series, series_rows in sorted(series_map.items()):
        def sort_key(item: dict[str, Any]) -> tuple[int, float | str]:
            try:
                return (0, float(item["x_value"]))
            except (TypeError, ValueError):
                return (1, str(item["x_value"]))
        ordered = sorted(series_rows, key=sort_key)
        xs, labels = _numeric_x(ordered)
        ys = [float(record["mean"]) for record in ordered]
        low = [float(record["confidence_interval_low"]) for record in ordered]
        high = [float(record["confidence_interval_high"]) for record in ordered]
        yerr = np.array(
            [
                [max(0.0, value - lower) for value, lower in zip(ys, low)],
                [max(0.0, upper - value) for value, upper in zip(ys, high)],
            ]
        )
        ax.errorbar(xs, ys, yerr=yerr, marker="o", capsize=2, label=series)
        if labels is not None:
            ax.set_xticks(xs, labels, rotation=20, ha="right")
    ax.set_title(title)
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize="small")


def render_campaign(campaign_id: str) -> dict[str, Any]:
    campaign_dir = CAMPAIGN_ROOT / campaign_id
    verification = verify_campaign(campaign_id)
    if not verification["verified"]:
        raise ValueError("unverified campaign cannot be rendered")
    aggregate_dir = campaign_dir / "aggregates"
    figures_dir = campaign_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {"campaign_id": campaign_id, "render_version": 2, "figures": {}}
    for panel_id in REQUIRED_PANELS:
        dataset = aggregate_dir / f"{panel_id}.csv"
        rows = _load_panel_csv(dataset)
        figure, axis = plt.subplots(figsize=(6.5, 4.2), dpi=300)
        _plot_panel(axis, rows, panel_id.replace("_", " ").title())
        axis.set_xlabel(str(rows[0]["x_variable"]).replace("_", " ").title())
        axis.set_ylabel(str(rows[0]["dependent_metric"]).replace("_", " ").title())
        figure.tight_layout()
        outputs: dict[str, str] = {}
        for extension in ("svg", "pdf", "png"):
            path = figures_dir / f"{panel_id}.{extension}"
            figure.savefig(path, dpi=300, bbox_inches="tight")
            outputs[extension] = str(path)
        plt.close(figure)
        manifest["figures"][panel_id] = {
            "aggregate_input_path": str(dataset),
            "aggregate_input_hash": _file_hash(dataset),
            "plotted_row_count": len(rows),
            "x_field": rows[0]["x_variable"],
            "y_field": rows[0]["dependent_metric"],
            "series_field": "series",
            "outputs": outputs,
            "output_hashes": {extension: _file_hash(Path(path)) for extension, path in outputs.items()},
        }
    for composite, panels in COMPOSITES.items():
        figure, axes = plt.subplots(len(panels), 1, figsize=(7.5, 3.6 * len(panels)), dpi=300)
        axis_list = list(np.ravel(axes)) if isinstance(axes, np.ndarray) else [axes]
        for axis, panel_id in zip(axis_list, panels, strict=True):
            rows = _load_panel_csv(aggregate_dir / f"{panel_id}.csv")
            _plot_panel(axis, rows, panel_id.replace("_", " ").title())
            axis.set_xlabel(str(rows[0]["x_variable"]).replace("_", " ").title())
            axis.set_ylabel(str(rows[0]["dependent_metric"]).replace("_", " ").title())
        figure.tight_layout()
        outputs: dict[str, str] = {}
        for extension in ("svg", "pdf", "png"):
            path = figures_dir / f"{composite}.{extension}"
            figure.savefig(path, dpi=300, bbox_inches="tight")
            outputs[extension] = str(path)
        plt.close(figure)
        manifest["figures"][composite] = {
            "panels": list(panels),
            "outputs": outputs,
            "output_hashes": {extension: _file_hash(Path(path)) for extension, path in outputs.items()},
        }
    manifest_path = figures_dir / "render_manifest.json"
    _write_json(manifest_path, manifest)
    return {"campaign_id": campaign_id, "render_manifest": str(manifest_path)}


def export_bundle(campaign_id: str) -> dict[str, Any]:
    campaign_dir = CAMPAIGN_ROOT / campaign_id
    verify_campaign(campaign_id)
    if not (campaign_dir / "figures" / "render_manifest.json").exists():
        render_campaign(campaign_id)
    bundle_dir = RELEASE_ROOT / f"{campaign_id}-bundle"
    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
    shutil.copytree(campaign_dir, bundle_dir)
    checksums: dict[str, str] = {}
    for path in sorted(bundle_dir.rglob("*")):
        if path.is_file() and path.name != "bundle_checksums.json":
            checksums[str(path.relative_to(bundle_dir))] = _file_hash(path)
    (bundle_dir / "bundle_checksums.json").write_text(
        json.dumps(checksums, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return {
        "campaign_id": campaign_id,
        "bundle_dir": str(bundle_dir),
        "bundle_hash": _hash(checksums),
        "file_count": len(checksums),
    }


def verify_bundle(bundle: Path) -> dict[str, Any]:
    if not bundle.exists():
        raise FileNotFoundError(bundle)
    with tempfile.TemporaryDirectory() as tmpdir:
        scratch = Path(tmpdir) / bundle.name
        shutil.copytree(bundle, scratch)
        checksum_path = scratch / "bundle_checksums.json"
        if not checksum_path.exists():
            raise FileNotFoundError("bundle_checksums.json")
        checksums = json.loads(checksum_path.read_text(encoding="utf-8"))
        actual_files = {
            str(path.relative_to(scratch))
            for path in scratch.rglob("*")
            if path.is_file() and path.name != "bundle_checksums.json"
        }
        if actual_files != set(checksums):
            raise ValueError("bundle file inventory differs from checksum manifest")
        for relpath, expected in checksums.items():
            actual = _file_hash(scratch / relpath)
            if actual != expected:
                raise ValueError(f"checksum mismatch: {relpath}")
    return {"bundle": str(bundle), "verified": True, "file_count": len(checksums)}
