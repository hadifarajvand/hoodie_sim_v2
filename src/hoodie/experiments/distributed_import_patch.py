from __future__ import annotations

from contextlib import contextmanager
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any


_INSTALLED = False


def _result_root(result_root: Path) -> Path:
    return result_root.parent if result_root.is_file() else result_root


def _bundle_path(result_root: Path) -> Path:
    return _result_root(result_root) / "result_bundle.json"


def _read_bundle(result_root: Path) -> dict[str, Any]:
    path = _bundle_path(result_root)
    if not path.is_file():
        raise FileNotFoundError(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"result bundle must contain a JSON object: {path}")
    return payload


def _preflight(campaign_id: str, result_root: Path) -> dict[str, Any]:
    from . import distributed_v2

    root = _result_root(result_root)
    distributed_v2._validate_checksums(root)
    payload = _read_bundle(root)
    if payload.get("campaign_id") != campaign_id:
        raise ValueError("result campaign ID mismatch")
    expected_hash = str(payload.get("result_hash", ""))
    hash_payload = {key: value for key, value in payload.items() if key != "result_hash"}
    if not expected_hash or distributed_v2._hash(hash_payload) != expected_hash:
        raise ValueError("result bundle hash mismatch")
    if payload.get("status") != "completed":
        raise RuntimeError(
            "refusing to import a non-completed shard result "
            f"(shard_id={payload.get('shard_id')}, status={payload.get('status')})"
        )
    job_ids = [str(value) for value in payload.get("job_ids", [])]
    job_results = payload.get("job_results", [])
    if not job_ids or not isinstance(job_results, list):
        raise ValueError("completed result bundle has no job inventory")
    result_by_id = {
        str(item.get("job_id")): item
        for item in job_results
        if isinstance(item, dict) and item.get("job_id")
    }
    if set(result_by_id) != set(job_ids):
        raise ValueError("result bundle does not contain exactly one result per job")
    if any(item.get("status") != "completed" for item in result_by_id.values()):
        raise RuntimeError("completed result bundle contains a non-completed job")

    job_plan = distributed_v2.CAMPAIGN_ROOT / campaign_id / "job_plan.json"
    if job_plan.is_file():
        planned = {
            str(row["job_id"])
            for row in json.loads(job_plan.read_text(encoding="utf-8"))
        }
        if not set(job_ids) <= planned:
            raise ValueError("result bundle contains jobs absent from campaign plan")

    output_root = root / "job_outputs"
    for job_id in job_ids:
        source = output_root / job_id
        status_path = source / "status.json"
        marker = source / "completion.marker"
        if not source.is_dir() or not status_path.is_file() or not marker.is_file():
            raise FileNotFoundError(
                f"completed result is missing job output inventory: {job_id}"
            )
        status = json.loads(status_path.read_text(encoding="utf-8"))
        if status.get("status") != "completed" or status.get("completion_marker") is not True:
            raise ValueError(f"job output is not scientifically complete: {job_id}")
    return payload


@contextmanager
def _campaign_import_lock(campaign_dir: Path):
    lock_path = campaign_dir / ".import.lock"
    campaign_dir.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise RuntimeError(f"another import owns campaign lock: {lock_path}") from exc
    try:
        os.write(descriptor, f"pid={os.getpid()}\n".encode())
        os.fsync(descriptor)
        yield
    finally:
        os.close(descriptor)
        lock_path.unlink(missing_ok=True)


def _hardlink_tree(source: Path, destination: Path) -> None:
    def link_file(src: str, dst: str) -> str:
        try:
            os.link(src, dst)
        except OSError as exc:
            raise OSError(
                "result import requires source and HOODIE_RUN_ROOT on the same "
                "filesystem so large checkpoints are not physically duplicated"
            ) from exc
        return dst

    shutil.copytree(source, destination, copy_function=link_file)


def _restore_bytes(path: Path, payload: bytes | None) -> None:
    if payload is None:
        path.unlink(missing_ok=True)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkstemp(prefix=f".{path.name}-", dir=path.parent)[1]
    )
    try:
        temporary.write_bytes(payload)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _import_one_locked(
    campaign_id: str,
    result_root: Path,
    payload: dict[str, Any],
) -> dict[str, Any]:
    from . import distributed_v2
    from . import production_campaign as production

    root = _result_root(result_root)
    campaign_dir = distributed_v2.CAMPAIGN_ROOT / campaign_id
    jobs_dir = campaign_dir / "jobs"
    imports_dir = campaign_dir / "shard_imports"
    staging_root = campaign_dir / ".import-staging"
    jobs_dir.mkdir(parents=True, exist_ok=True)
    imports_dir.mkdir(parents=True, exist_ok=True)
    staging_root.mkdir(parents=True, exist_ok=True)

    shard_id = str(payload["shard_id"])
    result_hash = str(payload["result_hash"])
    receipt_path = imports_dir / f"{shard_id}.json"
    if receipt_path.is_file():
        existing = json.loads(receipt_path.read_text(encoding="utf-8"))
        if existing.get("result_hash") != result_hash:
            raise ValueError("conflicting result for previously imported shard")
        return {
            "campaign_id": campaign_id,
            "shard_id": shard_id,
            "idempotent": True,
            "imported_jobs": 0,
        }

    job_ids = [str(value) for value in payload["job_ids"]]
    for job_id in job_ids:
        source = root / "job_outputs" / job_id
        destination = jobs_dir / job_id
        if destination.exists() and distributed_v2._directory_hash(destination) != distributed_v2._directory_hash(source):
            raise ValueError(f"conflicting imported job output: {job_id}")

    transaction_dir = Path(
        tempfile.mkdtemp(prefix=f"{shard_id}-", dir=staging_root)
    )
    staged_jobs = transaction_dir / "jobs"
    staged_jobs.mkdir()
    for job_id in job_ids:
        destination = jobs_dir / job_id
        if destination.exists():
            continue
        _hardlink_tree(root / "job_outputs" / job_id, staged_jobs / job_id)
        if distributed_v2._directory_hash(staged_jobs / job_id) != distributed_v2._directory_hash(root / "job_outputs" / job_id):
            raise ValueError(f"staged job hash mismatch: {job_id}")

    registry_path = campaign_dir / "checkpoint_registry.json"
    registry_before = registry_path.read_bytes() if registry_path.exists() else None
    receipt_before = receipt_path.read_bytes() if receipt_path.exists() else None
    moved: list[Path] = []
    try:
        for job_id in job_ids:
            staged = staged_jobs / job_id
            final = jobs_dir / job_id
            if staged.exists():
                os.replace(staged, final)
                moved.append(final)

        existing_registry = production._load_campaign_checkpoint_registry(campaign_dir)
        by_job = {
            str(record.get("training_job_id")): record
            for record in existing_registry
            if record.get("training_job_id")
        }
        for job_id in job_ids:
            selected = jobs_dir / job_id / "selected_checkpoint.json"
            if not selected.is_file():
                continue
            record = json.loads(selected.read_text(encoding="utf-8"))
            checkpoint_id = str(record["checkpoint_id"])
            checkpoint_path = (
                jobs_dir
                / job_id
                / "internal_checkpoints"
                / checkpoint_id
                / "checkpoint.pt"
            )
            if not checkpoint_path.is_file():
                raise FileNotFoundError(checkpoint_path)
            corrected = {
                **record,
                "checkpoint_path": str(checkpoint_path),
                "checkpoint_hash": distributed_v2._file_hash(checkpoint_path),
            }
            by_job[job_id] = corrected
            production._write_json(selected, corrected)
        production._write_campaign_checkpoint_registry(
            campaign_dir, list(by_job.values())
        )
        production._write_json(receipt_path, payload)
    except Exception:
        for path in reversed(moved):
            shutil.rmtree(path, ignore_errors=True)
        _restore_bytes(registry_path, registry_before)
        _restore_bytes(receipt_path, receipt_before)
        raise
    finally:
        shutil.rmtree(transaction_dir, ignore_errors=True)

    return {
        "campaign_id": campaign_id,
        "shard_id": shard_id,
        "imported_jobs": len(moved),
        "idempotent": False,
        "result_hash": result_hash,
    }


def import_shard_results_atomic(
    campaign_id: str, result_root: Path
) -> dict[str, Any]:
    from . import distributed_v2

    payload = _preflight(campaign_id, result_root)
    campaign_dir = distributed_v2.CAMPAIGN_ROOT / campaign_id
    with _campaign_import_lock(campaign_dir):
        return _import_one_locked(campaign_id, result_root, payload)


def import_results_directory_atomic(
    campaign_id: str, results_dir: Path
) -> dict[str, Any]:
    from . import distributed_v2

    bundle_paths = sorted(results_dir.rglob("result_bundle.json"))
    if not bundle_paths:
        raise FileNotFoundError(
            f"no result_bundle.json files found under {results_dir}"
        )

    prepared: list[tuple[Path, dict[str, Any]]] = []
    seen_shards: dict[str, Path] = {}
    seen_jobs: dict[str, str] = {}
    for bundle_path in bundle_paths:
        root = bundle_path.parent
        payload = _preflight(campaign_id, root)
        shard_id = str(payload["shard_id"])
        if shard_id in seen_shards:
            raise ValueError(
                f"duplicate result bundles for shard {shard_id}: "
                f"{seen_shards[shard_id]} and {root}"
            )
        seen_shards[shard_id] = root
        for job_id in (str(value) for value in payload["job_ids"]):
            prior = seen_jobs.get(job_id)
            if prior is not None:
                raise ValueError(
                    f"job {job_id} appears in multiple shard results: {prior}, {shard_id}"
                )
            seen_jobs[job_id] = shard_id
        prepared.append((root, payload))

    campaign_dir = distributed_v2.CAMPAIGN_ROOT / campaign_id
    jobs_dir = campaign_dir / "jobs"
    imports_dir = campaign_dir / "shard_imports"
    jobs_before = {
        path.name for path in jobs_dir.iterdir() if path.is_dir()
    } if jobs_dir.is_dir() else set()
    receipts_before = {
        path.name for path in imports_dir.glob("*.json")
    } if imports_dir.is_dir() else set()
    registry_path = campaign_dir / "checkpoint_registry.json"
    registry_before = registry_path.read_bytes() if registry_path.exists() else None

    imported: list[dict[str, Any]] = []
    with _campaign_import_lock(campaign_dir):
        try:
            for root, payload in prepared:
                imported.append(_import_one_locked(campaign_id, root, payload))
        except Exception:
            if jobs_dir.is_dir():
                for path in jobs_dir.iterdir():
                    if path.is_dir() and path.name not in jobs_before:
                        shutil.rmtree(path, ignore_errors=True)
            if imports_dir.is_dir():
                for path in imports_dir.glob("*.json"):
                    if path.name not in receipts_before:
                        path.unlink(missing_ok=True)
            _restore_bytes(registry_path, registry_before)
            raise
    return {
        "campaign_id": campaign_id,
        "imports": imported,
        "imported_shards": len(imported),
        "transactional": True,
    }


def install_distributed_import_patch() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    from . import distributed_v2

    distributed_v2.import_shard_results = import_shard_results_atomic
    distributed_v2.import_results_directory = import_results_directory_atomic
    _INSTALLED = True
