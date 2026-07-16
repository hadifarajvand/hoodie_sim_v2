from __future__ import annotations

from dataclasses import asdict, fields
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import shutil
import sys
import time
from typing import Any, Iterable

import torch

from .job_matrix import ProductionJobRow
from .matrix_patch import install_matrix_patch
from .production_patch import (
    CheckpointResolver,
    campaign_status,
    execute_matrix_job,
)
from . import production_campaign as production
from .scientific_pipeline import (
    aggregate_campaign,
    export_bundle,
    render_campaign,
    verify_campaign,
)

CAMPAIGN_ROOT = Path("artifacts/hoodie/campaigns")
DISTRIBUTED_ROOT = Path("artifacts/hoodie/distributed")
SOURCE_CONTRACT_PATH = Path(
    "artifacts/hoodie/source_contracts/figures_8_11_source_contract.json"
)


def _canonical(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _hash(payload: object) -> str:
    return sha256(_canonical(payload).encode("utf-8")).hexdigest()


def _file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read_rows(path: Path) -> list[ProductionJobRow]:
    allowed = {field.name for field in fields(ProductionJobRow)}
    return [
        ProductionJobRow(**{key: value for key, value in raw.items() if key in allowed})
        for raw in json.loads(path.read_text(encoding="utf-8"))
    ]


def _default_rows(campaign_id: str) -> list[ProductionJobRow]:
    install_matrix_patch()
    from . import job_matrix

    return job_matrix.build_production_job_matrix(campaign_id)


def _rows(campaign_id: str, matrix_path: Path | None = None) -> list[ProductionJobRow]:
    return _read_rows(matrix_path) if matrix_path is not None else _default_rows(campaign_id)


def _source_commit() -> str:
    return production._source_commit()


def _split_evenly(rows: list[ProductionJobRow], count: int) -> list[list[ProductionJobRow]]:
    if count <= 0:
        raise ValueError("shard count must be positive")
    buckets: list[list[ProductionJobRow]] = [[] for _ in range(min(count, max(1, len(rows))))]
    for index, row in enumerate(rows):
        buckets[index % len(buckets)].append(row)
    return [bucket for bucket in buckets if bucket]


def build_shard_plan(
    campaign_id: str,
    *,
    training_shards: int,
    evaluation_shards: int,
    matrix_path: Path | None = None,
) -> dict[str, Any]:
    rows = _rows(campaign_id, matrix_path)
    training = [row for row in rows if row.job_type == "training"]
    evaluation = [row for row in rows if row.job_type == "evaluation"]
    assignments: list[dict[str, Any]] = []
    for phase, phase_rows, shard_count in (
        ("training", training, training_shards),
        ("evaluation", evaluation, evaluation_shards),
    ):
        for index, bucket in enumerate(_split_evenly(phase_rows, shard_count), start=1):
            assignments.append(
                {
                    "shard_id": f"{phase}-{index:03d}",
                    "phase": phase,
                    "job_ids": [row.job_id for row in bucket],
                    "checkpoint_dependencies": sorted(
                        {row.checkpoint_dependency for row in bucket if row.checkpoint_dependency}
                    ),
                }
            )
    payload = {
        "schema_version": 2,
        "campaign_id": campaign_id,
        "source_commit": _source_commit(),
        "source_contract_hash": _file_hash(SOURCE_CONTRACT_PATH),
        "matrix_hash": _hash([asdict(row) for row in rows]),
        "total_jobs": len(rows),
        "training_jobs": len(training),
        "evaluation_jobs": len(evaluation),
        "rows": [asdict(row) for row in rows],
        "shard_assignments": assignments,
        "execution_order": ["training", "import-training", "evaluation", "import-evaluation", "finalize"],
        "created_at": time.time(),
    }
    payload["plan_hash"] = _hash(payload)
    return payload


def write_shard_plan(plan: dict[str, Any], output_path: Path) -> Path:
    _write_json(output_path, plan)
    return output_path


def _checksums(root: Path, *, exclude: Iterable[str] = ()) -> dict[str, str]:
    excluded = set(exclude)
    return {
        str(path.relative_to(root)): _file_hash(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and str(path.relative_to(root)) not in excluded
    }


def _validate_checksums(root: Path, manifest_name: str = "checksums.json") -> None:
    checksum_path = root / manifest_name
    if not checksum_path.exists():
        raise FileNotFoundError(checksum_path)
    expected = json.loads(checksum_path.read_text(encoding="utf-8"))
    actual_files = {
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_file() and str(path.relative_to(root)) != manifest_name
    }
    if actual_files != set(expected):
        missing = sorted(set(expected) - actual_files)
        unexpected = sorted(actual_files - set(expected))
        raise ValueError(f"bundle inventory mismatch; missing={missing}, unexpected={unexpected}")
    for relpath, digest in expected.items():
        if _file_hash(root / relpath) != digest:
            raise ValueError(f"checksum mismatch: {relpath}")


def _checkpoint_record(campaign_dir: Path, dependency: str) -> dict[str, Any]:
    registry_path = campaign_dir / "checkpoint_registry.json"
    if not registry_path.exists():
        raise FileNotFoundError("checkpoint registry is missing; import completed training shards first")
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    for record in registry.get("checkpoints", []):
        if record.get("training_job_id") == dependency and record.get("scientifically_complete"):
            path = Path(str(record["checkpoint_path"]))
            if not path.exists():
                raise FileNotFoundError(path)
            if record.get("checkpoint_hash") and _file_hash(path) != record["checkpoint_hash"]:
                raise ValueError(f"checkpoint hash mismatch: {dependency}")
            return record
    raise ValueError(f"checkpoint dependency is not available: {dependency}")


def export_shards(
    campaign_id: str,
    plan_path: Path,
    output_dir: Path,
    *,
    phase: str | None = None,
) -> list[Path]:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if plan["campaign_id"] != campaign_id:
        raise ValueError("plan campaign ID mismatch")
    if _hash({key: value for key, value in plan.items() if key != "plan_hash"}) != plan["plan_hash"]:
        raise ValueError("shard plan hash mismatch")
    rows = [ProductionJobRow(**row) for row in plan["rows"]]
    row_by_id = {row.job_id: row for row in rows}
    campaign_dir = CAMPAIGN_ROOT / campaign_id
    output_dir.mkdir(parents=True, exist_ok=True)
    bundles: list[Path] = []
    for assignment in plan["shard_assignments"]:
        if phase is not None and assignment["phase"] != phase:
            continue
        shard_dir = output_dir / assignment["shard_id"]
        if shard_dir.exists():
            shutil.rmtree(shard_dir)
        shard_dir.mkdir(parents=True)
        shard_rows = [row_by_id[job_id] for job_id in assignment["job_ids"]]
        snapshot = {
            "schema_version": 2,
            "campaign_id": campaign_id,
            "shard_id": assignment["shard_id"],
            "phase": assignment["phase"],
            "job_ids": assignment["job_ids"],
            "rows": [asdict(row) for row in shard_rows],
            "source_commit": plan["source_commit"],
            "source_contract_hash": plan["source_contract_hash"],
            "matrix_hash": plan["matrix_hash"],
            "plan_hash": plan["plan_hash"],
            "checkpoint_dependencies": assignment["checkpoint_dependencies"],
            "created_at": time.time(),
        }
        _write_json(shard_dir / "shard_manifest.json", snapshot)
        shutil.copy2(SOURCE_CONTRACT_PATH, shard_dir / "source_contract_snapshot.json")
        _write_json(
            shard_dir / "environment_manifest.json",
            {
                "python": sys.version.split()[0],
                "platform": platform.platform(),
                "pytorch": torch.__version__,
            },
        )
        checkpoint_records: list[dict[str, Any]] = []
        for dependency in assignment["checkpoint_dependencies"]:
            record = _checkpoint_record(campaign_dir, dependency)
            source = Path(str(record["checkpoint_path"]))
            destination = shard_dir / "checkpoints" / dependency / source.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            checkpoint_records.append(
                {**record, "checkpoint_path": str(destination.relative_to(shard_dir))}
            )
            metadata = source.parent / "metadata.json"
            if metadata.exists():
                shutil.copy2(metadata, destination.parent / "metadata.json")
        _write_json(shard_dir / "checkpoint_registry.json", {"checkpoints": checkpoint_records})
        _write_json(shard_dir / "checksums.json", _checksums(shard_dir, exclude=("checksums.json",)))
        bundles.append(shard_dir)
    return bundles


def _install_bundle_checkpoints(bundle_dir: Path, campaign_dir: Path) -> None:
    registry_path = bundle_dir / "checkpoint_registry.json"
    if not registry_path.exists():
        return
    records: list[dict[str, Any]] = []
    for record in json.loads(registry_path.read_text(encoding="utf-8")).get("checkpoints", []):
        source = bundle_dir / record["checkpoint_path"]
        destination = campaign_dir / "imported_checkpoints" / str(record["training_job_id"]) / source.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        metadata = source.parent / "metadata.json"
        if metadata.exists():
            shutil.copy2(metadata, destination.parent / "metadata.json")
        records.append({**record, "checkpoint_path": str(destination)})
    if records:
        production._write_json(
            campaign_dir / "checkpoint_registry.json",
            {"campaign_id": campaign_dir.name, "checkpoints": records},
        )


def run_shard(
    bundle_dir: Path,
    work_dir: Path,
    *,
    max_runtime_seconds: float | None = None,
) -> dict[str, Any]:
    _validate_checksums(bundle_dir)
    manifest = json.loads((bundle_dir / "shard_manifest.json").read_text(encoding="utf-8"))
    rows = [ProductionJobRow(**row) for row in manifest["rows"]]
    campaign_dir = work_dir / manifest["campaign_id"]
    campaign_dir.mkdir(parents=True, exist_ok=True)
    _install_bundle_checkpoints(bundle_dir, campaign_dir)
    resolver = CheckpointResolver(campaign_dir)
    results: list[dict[str, Any]] = []
    start = time.time()
    for row in rows:
        remaining = None
        if max_runtime_seconds is not None:
            remaining = max_runtime_seconds - (time.time() - start)
            if remaining <= 0:
                break
        result = execute_matrix_job(
            row=row,
            campaign_dir=campaign_dir,
            source_commit=str(manifest["source_commit"]),
            max_runtime_seconds=remaining,
            checkpoint_resolver=resolver,
        )
        results.append(
            {
                "job_id": result.job_id,
                "status": result.status,
                "checkpoint_id": result.checkpoint_id,
                "trace_hash": result.trace_hash,
            }
        )
        if result.status != "completed":
            break
    result_root = work_dir / "results" / manifest["shard_id"]
    if result_root.exists():
        shutil.rmtree(result_root)
    job_output_root = result_root / "job_outputs"
    job_output_root.mkdir(parents=True)
    for row in rows:
        source = campaign_dir / "jobs" / row.job_id
        if source.exists():
            shutil.copytree(source, job_output_root / row.job_id)
    registry = campaign_dir / "checkpoint_registry.json"
    if registry.exists():
        shutil.copy2(registry, result_root / "checkpoint_registry.json")
    all_complete = len(results) == len(rows) and all(item["status"] == "completed" for item in results)
    bundle = {
        "schema_version": 2,
        "campaign_id": manifest["campaign_id"],
        "shard_id": manifest["shard_id"],
        "phase": manifest["phase"],
        "plan_hash": manifest["plan_hash"],
        "source_commit": manifest["source_commit"],
        "source_contract_hash": manifest["source_contract_hash"],
        "matrix_hash": manifest["matrix_hash"],
        "job_ids": manifest["job_ids"],
        "job_results": results,
        "status": "completed" if all_complete else "interrupted_resumable",
        "environment": {
            "hostname": platform.node(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "pytorch": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "mps_available": bool(
                getattr(torch.backends, "mps", None) is not None
                and torch.backends.mps.is_available()
            ),
        },
        "created_at": time.time(),
    }
    bundle["result_hash"] = _hash(bundle)
    _write_json(result_root / "result_bundle.json", bundle)
    _write_json(result_root / "checksums.json", _checksums(result_root, exclude=("checksums.json",)))
    return bundle


def _directory_hash(path: Path) -> str:
    return _hash(_checksums(path))


def import_shard_results(campaign_id: str, result_root: Path) -> dict[str, Any]:
    _validate_checksums(result_root)
    payload = json.loads((result_root / "result_bundle.json").read_text(encoding="utf-8"))
    if payload["campaign_id"] != campaign_id:
        raise ValueError("result campaign ID mismatch")
    expected_hash = payload.pop("result_hash")
    if _hash(payload) != expected_hash:
        raise ValueError("result bundle hash mismatch")
    payload["result_hash"] = expected_hash
    campaign_dir = CAMPAIGN_ROOT / campaign_id
    campaign_dir.mkdir(parents=True, exist_ok=True)
    imports_dir = campaign_dir / "shard_imports"
    imports_dir.mkdir(parents=True, exist_ok=True)
    import_record = imports_dir / f"{payload['shard_id']}.json"
    if import_record.exists():
        existing = json.loads(import_record.read_text(encoding="utf-8"))
        if existing.get("result_hash") != expected_hash:
            raise ValueError("conflicting result for previously imported shard")
        return {"campaign_id": campaign_id, "shard_id": payload["shard_id"], "idempotent": True}
    for job_id in payload["job_ids"]:
        source = result_root / "job_outputs" / job_id
        if not source.exists():
            continue
        destination = campaign_dir / "jobs" / job_id
        if destination.exists():
            if _directory_hash(destination) != _directory_hash(source):
                raise ValueError(f"conflicting imported job output: {job_id}")
        else:
            shutil.copytree(source, destination)
    # Rebuild central checkpoint records from the imported training job outputs.
    central_records = production._load_campaign_checkpoint_registry(campaign_dir)
    by_job = {record.get("training_job_id"): record for record in central_records}
    for job_id in payload["job_ids"]:
        selected = campaign_dir / "jobs" / job_id / "selected_checkpoint.json"
        if not selected.exists():
            continue
        record = json.loads(selected.read_text(encoding="utf-8"))
        checkpoint_id = str(record["checkpoint_id"])
        checkpoint_path = campaign_dir / "jobs" / job_id / "internal_checkpoints" / checkpoint_id / "checkpoint.pt"
        if not checkpoint_path.exists():
            raise FileNotFoundError(checkpoint_path)
        corrected = {
            **record,
            "checkpoint_path": str(checkpoint_path),
            "checkpoint_hash": _file_hash(checkpoint_path),
        }
        by_job[job_id] = corrected
        production._write_json(selected, corrected)
    production._write_campaign_checkpoint_registry(campaign_dir, list(by_job.values()))
    _write_json(import_record, payload)
    return {
        "campaign_id": campaign_id,
        "shard_id": payload["shard_id"],
        "imported_jobs": len(payload["job_ids"]),
        "idempotent": False,
    }


def import_results_directory(campaign_id: str, results_dir: Path) -> dict[str, Any]:
    imported: list[dict[str, Any]] = []
    failures: list[str] = []
    for bundle in sorted(results_dir.rglob("result_bundle.json")):
        try:
            imported.append(import_shard_results(campaign_id, bundle.parent))
        except Exception as exc:
            failures.append(f"{bundle}: {exc}")
    if failures:
        raise ValueError("result import failures: " + "; ".join(failures))
    return {"campaign_id": campaign_id, "imports": imported, "imported_shards": len(imported)}


def shard_status(campaign_id: str) -> dict[str, Any]:
    return campaign_status(campaign_id, CAMPAIGN_ROOT)


def backend_provenance_audit(campaign_id: str) -> dict[str, Any]:
    campaign_dir = CAMPAIGN_ROOT / campaign_id
    records = production._load_campaign_checkpoint_registry(campaign_dir)
    backends = sorted({str(record.get("backend_type", "legacy_unknown")) for record in records})
    devices = sorted({str(record.get("device_string", "unknown")) for record in records})
    payload = {
        "campaign_id": campaign_id,
        "checkpoint_count": len(records),
        "checkpoint_backends": backends,
        "checkpoint_devices": devices,
        "current_environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "pytorch": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "mps_available": bool(
                getattr(torch.backends, "mps", None) is not None
                and torch.backends.mps.is_available()
            ),
        },
        "portable_checkpoint_loading": True,
        "legacy_unknown_is_never_relabelled": True,
    }
    output = Path("artifacts/hoodie/implementation_run/campaign/backend_provenance_audit_v2.json")
    _write_json(output, payload)
    return payload


def resource_plan(campaign_id: str, matrix_path: Path | None = None) -> dict[str, Any]:
    rows = _rows(campaign_id, matrix_path)
    return {
        "campaign_id": campaign_id,
        "total_jobs": len(rows),
        "training_jobs": sum(row.job_type == "training" for row in rows),
        "evaluation_jobs": sum(row.job_type == "evaluation" for row in rows),
        "training_episode_total": sum(int(row.training_contract.get("training_episodes", 0)) for row in rows),
        "evaluation_episode_total": sum(int(row.evaluation_contract.get("validation_episodes", 0)) for row in rows),
        "runtime_estimate": None,
        "note": "No wall-clock estimate is fabricated. Benchmark one representative training and evaluation job on the assigned backend before sizing workers.",
    }


def finalize(campaign_id: str) -> dict[str, Any]:
    status = shard_status(campaign_id)
    if status.get("completed_jobs") != status.get("total"):
        raise RuntimeError(f"campaign is incomplete and cannot be finalized: {status}")
    aggregation = aggregate_campaign(campaign_id)
    verification = verify_campaign(campaign_id)
    rendering = render_campaign(campaign_id)
    release = export_bundle(campaign_id)
    return {
        "campaign_id": campaign_id,
        "status": status,
        "aggregation": aggregation,
        "verification": verification,
        "rendering": rendering,
        "release": release,
    }
