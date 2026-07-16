from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

_INSTALLED = False
_ORIGINAL_IMPORT_SHARD_RESULTS: Callable[[str, Path], dict[str, Any]] | None = None
_ORIGINAL_IMPORT_RESULTS_DIRECTORY: Callable[[str, Path], dict[str, Any]] | None = None


def _result_bundle_path(result_root: Path) -> Path:
    root = result_root.parent if result_root.is_file() else result_root
    return root / "result_bundle.json"


def _read_result_bundle(result_root: Path) -> dict[str, Any]:
    bundle_path = _result_bundle_path(result_root)
    if not bundle_path.exists():
        raise FileNotFoundError(bundle_path)
    payload = json.loads(bundle_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(
            f"result bundle must contain a JSON object: {bundle_path}"
        )
    return payload


def _require_completed_result(
    campaign_id: str, result_root: Path
) -> dict[str, Any]:
    payload = _read_result_bundle(result_root)
    if payload.get("campaign_id") != campaign_id:
        raise ValueError("result campaign ID mismatch")
    status = str(payload.get("status", "unknown"))
    if status != "completed":
        shard_id = str(payload.get("shard_id", "unknown"))
        raise RuntimeError(
            "refusing to import a non-completed shard result "
            f"(shard_id={shard_id}, status={status}); preserve the worker work directory "
            "and resume the same shard until it produces a completed result bundle"
        )
    job_results = payload.get("job_results")
    if isinstance(job_results, list) and any(
        not isinstance(result, dict) or result.get("status") != "completed"
        for result in job_results
    ):
        raise RuntimeError(
            "result bundle claims completion but contains a non-completed job result"
        )
    job_ids = payload.get("job_ids")
    if isinstance(job_ids, list) and isinstance(job_results, list):
        result_ids = [
            str(result.get("job_id"))
            for result in job_results
            if isinstance(result, dict)
        ]
        if sorted(str(job_id) for job_id in job_ids) != sorted(result_ids):
            raise RuntimeError(
                "completed result bundle does not contain exactly one result for every shard job"
            )
    return payload


def import_shard_results_completed_only(
    campaign_id: str, result_root: Path
) -> dict[str, Any]:
    """Reject partial shard bundles before the canonical campaign can be mutated."""

    _require_completed_result(campaign_id, result_root)
    if _ORIGINAL_IMPORT_SHARD_RESULTS is None:  # pragma: no cover
        raise RuntimeError("distributed import patch is not installed")
    root = result_root.parent if result_root.is_file() else result_root
    return _ORIGINAL_IMPORT_SHARD_RESULTS(campaign_id, root)


def import_results_directory_completed_only(
    campaign_id: str, results_dir: Path
) -> dict[str, Any]:
    """Preflight completion and shard identity before starting a bulk import."""

    bundle_paths = sorted(results_dir.rglob("result_bundle.json"))
    if not bundle_paths:
        raise FileNotFoundError(
            f"no result_bundle.json files found under {results_dir}"
        )

    incomplete: list[str] = []
    seen_shards: dict[str, Path] = {}
    for bundle_path in bundle_paths:
        payload = _read_result_bundle(bundle_path)
        if payload.get("campaign_id") != campaign_id:
            raise ValueError(f"result campaign ID mismatch: {bundle_path}")
        shard_id = str(payload.get("shard_id", "unknown"))
        prior = seen_shards.get(shard_id)
        if prior is not None:
            raise ValueError(
                f"duplicate result bundles for shard {shard_id}: {prior} and {bundle_path.parent}"
            )
        seen_shards[shard_id] = bundle_path.parent
        try:
            _require_completed_result(campaign_id, bundle_path.parent)
        except RuntimeError as exc:
            incomplete.append(f"{bundle_path.parent} ({exc})")
    if incomplete:
        raise RuntimeError(
            "refusing bulk import because invalid or non-completed shard results are present: "
            + "; ".join(incomplete)
        )
    if _ORIGINAL_IMPORT_RESULTS_DIRECTORY is None:  # pragma: no cover
        raise RuntimeError("distributed import patch is not installed")
    return _ORIGINAL_IMPORT_RESULTS_DIRECTORY(campaign_id, results_dir)


def install_distributed_import_patch() -> None:
    global _INSTALLED
    global _ORIGINAL_IMPORT_SHARD_RESULTS
    global _ORIGINAL_IMPORT_RESULTS_DIRECTORY

    if _INSTALLED:
        return

    from . import distributed_v2

    _ORIGINAL_IMPORT_SHARD_RESULTS = distributed_v2.import_shard_results
    _ORIGINAL_IMPORT_RESULTS_DIRECTORY = distributed_v2.import_results_directory
    distributed_v2.import_shard_results = import_shard_results_completed_only
    distributed_v2.import_results_directory = import_results_directory_completed_only
    _INSTALLED = True
