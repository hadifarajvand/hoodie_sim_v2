from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any


_REQUIRED_ROOT_FILES = (
    "job_plan.json",
    "checkpoint_registry.json",
    "aggregation_manifest.json",
    "verification_report.json",
    "fairness_report.json",
    "scientific_sanity_report.json",
    "lineage_report.json",
    "final_verification.json",
)
_REQUIRED_JOB_SUFFIXES = (
    ".csv",
    ".json",
    ".marker",
)


def _file_hash(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _tree_hash(checksums: dict[str, str]) -> str:
    payload = json.dumps(checksums, sort_keys=True, separators=(",", ":"))
    return sha256(payload.encode("utf-8")).hexdigest()


def _link_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(source, destination)
    except OSError as exc:
        raise OSError(
            "release bundle requires same-filesystem hard links to avoid duplicating "
            f"large scientific outputs: {source} -> {destination}"
        ) from exc


def _selected_bundle_files(campaign_dir: Path) -> list[Path]:
    selected: set[Path] = set()
    for name in _REQUIRED_ROOT_FILES:
        path = campaign_dir / name
        if not path.is_file():
            raise FileNotFoundError(path)
        selected.add(path)

    for directory in (campaign_dir / "aggregates", campaign_dir / "figures"):
        if not directory.is_dir():
            raise FileNotFoundError(directory)
        selected.update(path for path in directory.rglob("*") if path.is_file())

    jobs_dir = campaign_dir / "jobs"
    if not jobs_dir.is_dir():
        raise FileNotFoundError(jobs_dir)
    for job_dir in sorted(path for path in jobs_dir.iterdir() if path.is_dir()):
        status_path = job_dir / "status.json"
        marker_path = job_dir / "completion.marker"
        if not status_path.is_file() or not marker_path.is_file():
            raise ValueError(f"release bundle refuses incomplete job: {job_dir.name}")
        status = json.loads(status_path.read_text(encoding="utf-8"))
        if status.get("status") != "completed":
            raise ValueError(f"release bundle refuses non-completed job: {job_dir.name}")
        for path in job_dir.iterdir():
            if path.is_file() and (
                path.suffix in _REQUIRED_JOB_SUFFIXES
                or path.name in {"completion.marker"}
            ):
                selected.add(path)
        selected_checkpoint = job_dir / "selected_checkpoint.json"
        if selected_checkpoint.is_file():
            record = json.loads(selected_checkpoint.read_text(encoding="utf-8"))
            checkpoint_id = str(record["checkpoint_id"])
            checkpoint_dir = job_dir / "internal_checkpoints" / checkpoint_id
            for path in checkpoint_dir.rglob("*"):
                if path.is_file():
                    selected.add(path)
            retention = job_dir / "checkpoint_retention_manifest.json"
            if retention.is_file():
                selected.add(retention)
    return sorted(selected)


def verify_bundle(bundle: Path) -> dict[str, Any]:
    bundle = bundle.resolve()
    if not bundle.is_dir():
        raise FileNotFoundError(bundle)
    checksum_path = bundle / "bundle_checksums.json"
    if not checksum_path.is_file():
        raise FileNotFoundError(checksum_path)
    checksums = json.loads(checksum_path.read_text(encoding="utf-8"))
    if not isinstance(checksums, dict):
        raise ValueError("bundle_checksums.json must contain an object")
    actual_files = {
        str(path.relative_to(bundle))
        for path in bundle.rglob("*")
        if path.is_file() and path.name != "bundle_checksums.json"
    }
    if actual_files != set(checksums):
        raise ValueError("bundle file inventory differs from checksum manifest")
    for relative, expected in checksums.items():
        path = bundle / relative
        actual = _file_hash(path)
        if actual != expected:
            raise ValueError(f"bundle checksum mismatch: {relative}")
    return {
        "bundle": str(bundle),
        "verified": True,
        "file_count": len(checksums),
        "bundle_hash": _tree_hash(checksums),
    }


def export_bundle(campaign_id: str) -> dict[str, Any]:
    from . import scientific_pipeline as pipeline

    campaign_dir = (pipeline.CAMPAIGN_ROOT / campaign_id).resolve()
    verification = pipeline.verify_campaign(campaign_id)
    if not verification.get("verified") or not verification.get(
        "render_outputs_checked"
    ):
        raise ValueError(
            "release export requires successful post-render scientific verification"
        )
    release_root = pipeline.RELEASE_ROOT.resolve()
    release_root.mkdir(parents=True, exist_ok=True)
    destination = release_root / f"{campaign_id}-bundle"
    if destination.exists():
        verified = verify_bundle(destination)
        return {"campaign_id": campaign_id, **verified, "idempotent": True}

    selected = _selected_bundle_files(campaign_dir)
    temporary = Path(
        tempfile.mkdtemp(prefix=f".{campaign_id}-bundle-", dir=release_root)
    )
    try:
        checksums: dict[str, str] = {}
        for source in selected:
            relative = source.relative_to(campaign_dir)
            target = temporary / relative
            _link_file(source, target)
            checksums[str(relative)] = _file_hash(source)
        checksum_path = temporary / "bundle_checksums.json"
        checksum_path.write_text(
            json.dumps(checksums, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        verify_bundle(temporary)
        os.replace(temporary, destination)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    verified = verify_bundle(destination)
    return {"campaign_id": campaign_id, **verified, "idempotent": False}


def finalize(campaign_id: str) -> dict[str, Any]:
    from . import distributed_v2
    from . import scientific_pipeline as pipeline

    status = distributed_v2.shard_status(campaign_id)
    if status.get("completed_jobs") != status.get("total"):
        raise RuntimeError(
            f"campaign is incomplete and cannot be finalized: {status}"
        )
    if any(
        int(status.get(key, 0) or 0)
        for key in (
            "failed_jobs",
            "interrupted_jobs",
            "pending_jobs",
            "blocked_jobs",
            "scientifically_incomplete_jobs",
        )
    ):
        raise RuntimeError(f"campaign contains non-completed states: {status}")

    aggregation = pipeline.aggregate_campaign(campaign_id)
    pre_render_verification = pipeline.verify_campaign(campaign_id)
    rendering = pipeline.render_campaign(campaign_id)
    post_render_verification = pipeline.verify_campaign(campaign_id)
    if not post_render_verification.get("render_outputs_checked"):
        raise RuntimeError("post-render verification did not inspect rendered outputs")
    release = export_bundle(campaign_id)
    bundle_verification = verify_bundle(Path(release["bundle"]))
    return {
        "campaign_id": campaign_id,
        "status": status,
        "aggregation": aggregation,
        "pre_render_verification": pre_render_verification,
        "rendering": rendering,
        "post_render_verification": post_render_verification,
        "release": release,
        "bundle_verification": bundle_verification,
    }


def install_finalization_patch() -> None:
    from . import distributed_v2, scientific_pipeline

    scientific_pipeline.export_bundle = export_bundle
    scientific_pipeline.verify_bundle = verify_bundle
    distributed_v2.export_bundle = export_bundle
    distributed_v2.verify_bundle = verify_bundle
    distributed_v2.finalize = finalize
