from __future__ import annotations

from dataclasses import asdict
import json
import os
from pathlib import Path
import platform
import shutil
import tempfile
import time
from typing import Any

import torch

from .job_matrix import ProductionJobRow


_INSTALLED = False


def _hardlink(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(source, destination)
    except OSError as exc:
        raise OSError(
            "source and destination must be on the same filesystem so a large "
            f"checkpoint is not duplicated: {source} -> {destination}"
        ) from exc


def _hardlink_tree(source: Path, destination: Path) -> None:
    def link_file(src: str, dst: str) -> str:
        _hardlink(Path(src), Path(dst))
        return dst

    shutil.copytree(source, destination, copy_function=link_file)


def _require_empty_destination(path: Path) -> None:
    if not path.exists():
        return
    if not path.is_dir():
        raise FileExistsError(path)
    if any(path.iterdir()):
        raise FileExistsError(
            f"refusing to overwrite nonempty distributed output directory: {path}"
        )


def export_shards_storage_safe(
    campaign_id: str,
    plan_path: Path,
    output_dir: Path,
    *,
    phase: str | None = None,
) -> list[Path]:
    from . import distributed_v2

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if plan["campaign_id"] != campaign_id:
        raise ValueError("plan campaign ID mismatch")
    if (
        distributed_v2._hash(
            {key: value for key, value in plan.items() if key != "plan_hash"}
        )
        != plan["plan_hash"]
    ):
        raise ValueError("shard plan hash mismatch")

    _require_empty_destination(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = [ProductionJobRow(**row) for row in plan["rows"]]
    row_by_id = {row.job_id: row for row in rows}
    campaign_dir = distributed_v2.CAMPAIGN_ROOT / campaign_id
    bundles: list[Path] = []

    for assignment in plan["shard_assignments"]:
        if phase is not None and assignment["phase"] != phase:
            continue
        shard_dir = output_dir / assignment["shard_id"]
        if shard_dir.exists():
            raise FileExistsError(shard_dir)
        shard_dir.mkdir(parents=True)
        shard_rows = [row_by_id[job_id] for job_id in assignment["job_ids"]]
        snapshot = {
            "schema_version": 3,
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
            "checkpoint_transport": "same-filesystem-hardlink",
            "created_at": time.time(),
        }
        distributed_v2._write_json(shard_dir / "shard_manifest.json", snapshot)
        shutil.copy2(
            distributed_v2.SOURCE_CONTRACT_PATH,
            shard_dir / "source_contract_snapshot.json",
        )
        distributed_v2._write_json(
            shard_dir / "environment_manifest.json",
            {
                "python": platform.python_version(),
                "platform": platform.platform(),
                "pytorch": torch.__version__,
            },
        )
        checkpoint_records: list[dict[str, Any]] = []
        for dependency in assignment["checkpoint_dependencies"]:
            record = distributed_v2._checkpoint_record(campaign_dir, dependency)
            source = Path(str(record["checkpoint_path"]))
            destination = shard_dir / "checkpoints" / dependency / source.name
            _hardlink(source, destination)
            checkpoint_records.append(
                {
                    **record,
                    "checkpoint_path": str(destination.relative_to(shard_dir)),
                    "transport_sha256": distributed_v2._file_hash(destination),
                }
            )
            metadata = source.parent / "metadata.json"
            if metadata.is_file():
                shutil.copy2(metadata, destination.parent / "metadata.json")
        distributed_v2._write_json(
            shard_dir / "checkpoint_registry.json",
            {"checkpoints": checkpoint_records},
        )
        distributed_v2._write_json(
            shard_dir / "checksums.json",
            distributed_v2._checksums(shard_dir, exclude=("checksums.json",)),
        )
        distributed_v2._validate_checksums(shard_dir)
        bundles.append(shard_dir)
    return bundles


def install_bundle_checkpoints_without_copy(
    bundle_dir: Path, campaign_dir: Path
) -> None:
    """Register immutable bundle checkpoints in place instead of copying them."""

    from . import production_campaign as production

    registry_path = bundle_dir / "checkpoint_registry.json"
    if not registry_path.is_file():
        return
    records: list[dict[str, Any]] = []
    for record in json.loads(registry_path.read_text(encoding="utf-8")).get(
        "checkpoints", []
    ):
        source = (bundle_dir / str(record["checkpoint_path"])).resolve()
        if bundle_dir.resolve() not in source.parents:
            raise ValueError("bundle checkpoint path escapes bundle directory")
        if not source.is_file():
            raise FileNotFoundError(source)
        actual = sha256_file(source)
        expected = str(record.get("checkpoint_hash", ""))
        if expected and actual != expected:
            raise ValueError(
                f"bundle checkpoint hash mismatch: {record.get('training_job_id')}"
            )
        records.append({**record, "checkpoint_path": str(source)})
    if records:
        production._write_json(
            campaign_dir / "checkpoint_registry.json",
            {"campaign_id": campaign_dir.name, "checkpoints": records},
        )


def sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _replace_derived_result_root(staged: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    backup: Path | None = None
    if destination.exists():
        backup = destination.parent / f".{destination.name}-previous-{time.time_ns()}"
        os.replace(destination, backup)
    try:
        os.replace(staged, destination)
    except Exception:
        if backup is not None and backup.exists():
            os.replace(backup, destination)
        raise
    if backup is not None:
        shutil.rmtree(backup, ignore_errors=True)


def run_shard_storage_safe(
    bundle_dir: Path,
    work_dir: Path,
    *,
    max_runtime_seconds: float | None = None,
) -> dict[str, Any]:
    from . import distributed_v2
    from .production_patch import CheckpointResolver, execute_matrix_job

    distributed_v2._validate_checksums(bundle_dir)
    manifest = json.loads(
        (bundle_dir / "shard_manifest.json").read_text(encoding="utf-8")
    )
    rows = [ProductionJobRow(**row) for row in manifest["rows"]]
    if [row.job_id for row in rows] != [str(value) for value in manifest["job_ids"]]:
        raise ValueError("shard row order does not match job inventory")

    campaign_dir = work_dir / manifest["campaign_id"]
    campaign_dir.mkdir(parents=True, exist_ok=True)
    install_bundle_checkpoints_without_copy(bundle_dir, campaign_dir)
    resolver = CheckpointResolver(campaign_dir)
    results: list[dict[str, Any]] = []
    started = time.time()
    for row in rows:
        remaining = None
        if max_runtime_seconds is not None:
            remaining = max_runtime_seconds - (time.time() - started)
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

    all_complete = len(results) == len(rows) and all(
        item["status"] == "completed" for item in results
    )
    result_parent = work_dir / "results"
    result_parent.mkdir(parents=True, exist_ok=True)
    staged = Path(
        tempfile.mkdtemp(prefix=f".{manifest['shard_id']}-", dir=result_parent)
    )
    try:
        job_output_root = staged / "job_outputs"
        job_output_root.mkdir()
        for row in rows:
            source = campaign_dir / "jobs" / row.job_id
            if source.exists():
                _hardlink_tree(source, job_output_root / row.job_id)
        registry = campaign_dir / "checkpoint_registry.json"
        if registry.is_file():
            shutil.copy2(registry, staged / "checkpoint_registry.json")
        bundle = {
            "schema_version": 3,
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
            "result_transport": "same-filesystem-hardlink",
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
        bundle["result_hash"] = distributed_v2._hash(bundle)
        distributed_v2._write_json(staged / "result_bundle.json", bundle)
        distributed_v2._write_json(
            staged / "checksums.json",
            distributed_v2._checksums(staged, exclude=("checksums.json",)),
        )
        distributed_v2._validate_checksums(staged)
        destination = result_parent / manifest["shard_id"]
        _replace_derived_result_root(staged, destination)
        staged = Path()
        return bundle
    finally:
        if staged and staged.exists() and staged.is_dir():
            shutil.rmtree(staged, ignore_errors=True)


def install_distributed_storage_patch() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    from . import distributed_v2

    distributed_v2.export_shards = export_shards_storage_safe
    distributed_v2._install_bundle_checkpoints = install_bundle_checkpoints_without_copy
    distributed_v2.run_shard = run_shard_storage_safe
    _INSTALLED = True
