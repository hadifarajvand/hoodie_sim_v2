from __future__ import annotations

from contextlib import contextmanager
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from typing import Any, Iterator

from .campaign import campaign_status
from .campaign_layout import CampaignLayout, record_stage
from . import distributed_v2
from . import scientific_pipeline


def _file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _source_sha(layout: CampaignLayout) -> str:
    configured = os.environ.get("GITHUB_SHA")
    if configured:
        return configured
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=layout.repository_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    return completed.stdout.strip() or "unknown"


def _write_sha256sums(root: Path) -> Path:
    """Write a shell-verifiable sidecar without creating a checksum cycle."""

    root.mkdir(parents=True, exist_ok=True)
    canonical_inventory = root / "bundle_checksums.json"
    entries: list[str] = []
    for path in sorted(root.rglob("*")):
        if (
            not path.is_file()
            or path == canonical_inventory
            or path.name == "SHA256SUMS"
        ):
            continue
        relative = path.relative_to(root).as_posix()
        entries.append(f"{_file_hash(path)}  {relative}")
    output = root / "SHA256SUMS"
    output.write_text(
        "\n".join(entries) + ("\n" if entries else ""), encoding="utf-8"
    )
    return output


def _seal_bundle(root: Path) -> Path:
    """Keep bundle_checksums.json and SHA256SUMS mutually consistent."""

    inventory_path = root / "bundle_checksums.json"
    if not inventory_path.exists():
        raise FileNotFoundError(inventory_path)
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    if not isinstance(inventory, dict):
        raise ValueError(f"bundle inventory must be a JSON object: {inventory_path}")

    checksum_path = _write_sha256sums(root)
    inventory[checksum_path.name] = _file_hash(checksum_path)
    inventory_path.write_text(
        json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    scientific_pipeline.verify_bundle(root)
    return checksum_path


def _seal_result(layout: CampaignLayout, result: dict[str, Any]) -> dict[str, Any]:
    bundle_dir = Path(str(result["bundle_dir"])).expanduser().resolve(strict=False)
    expected = (layout.bundles_dir / f"{layout.campaign_id}-bundle").resolve(
        strict=False
    )
    if bundle_dir != expected:
        raise RuntimeError(
            f"bundle was written outside the resolved release directory: "
            f"expected={expected}, actual={bundle_dir}"
        )
    checksum_path = _seal_bundle(bundle_dir)
    inventory_path = bundle_dir / "bundle_checksums.json"
    return {
        **result,
        "preseal_bundle_hash": result.get("bundle_hash"),
        "bundle_hash": _file_hash(inventory_path),
        "bundle_dir": str(bundle_dir),
        "bundle_checksums": str(inventory_path),
        "sha256sums": str(checksum_path),
    }


@contextmanager
def _bound_pipeline(layout: CampaignLayout) -> Iterator[None]:
    """Bind legacy path-only helpers to one explicit external layout."""

    previous = (
        scientific_pipeline.CAMPAIGN_ROOT,
        scientific_pipeline.RELEASE_ROOT,
        distributed_v2.CAMPAIGN_ROOT,
    )
    scientific_pipeline.CAMPAIGN_ROOT = layout.campaign_root.parent
    scientific_pipeline.RELEASE_ROOT = layout.bundles_dir
    distributed_v2.CAMPAIGN_ROOT = layout.campaign_root.parent
    try:
        yield
    finally:
        (
            scientific_pipeline.CAMPAIGN_ROOT,
            scientific_pipeline.RELEASE_ROOT,
            distributed_v2.CAMPAIGN_ROOT,
        ) = previous


def _stage(layout: CampaignLayout, name: str, operation) -> dict[str, Any]:
    started = time.time()
    source_sha = _source_sha(layout)
    record_stage(
        layout,
        name,
        status="running",
        details={
            "started_at": started,
            "campaign_root": str(layout.campaign_root),
            "postprocessing_commit_sha": source_sha,
        },
    )
    try:
        with _bound_pipeline(layout):
            result = operation()
    except Exception as exc:
        record_stage(
            layout,
            name,
            status="failed",
            details={
                "started_at": started,
                "finished_at": time.time(),
                "error_type": exc.__class__.__name__,
                "error": str(exc),
                "campaign_root": str(layout.campaign_root),
                "postprocessing_commit_sha": source_sha,
            },
        )
        raise

    payload = dict(result)
    payload["campaign_root"] = str(layout.campaign_root)
    record_stage(
        layout,
        name,
        status="completed",
        details={
            "started_at": started,
            "finished_at": time.time(),
            "result": payload,
            "campaign_root": str(layout.campaign_root),
            "postprocessing_commit_sha": source_sha,
        },
    )
    return payload


def aggregate_campaign(layout: CampaignLayout) -> dict[str, Any]:
    return _stage(
        layout,
        "aggregate",
        lambda: scientific_pipeline.aggregate_campaign(layout.campaign_id),
    )


def verify_campaign(layout: CampaignLayout) -> dict[str, Any]:
    return _stage(
        layout,
        "verify",
        lambda: scientific_pipeline.verify_campaign(layout.campaign_id),
    )


def render_campaign(layout: CampaignLayout) -> dict[str, Any]:
    return _stage(
        layout,
        "render",
        lambda: scientific_pipeline.render_campaign(layout.campaign_id),
    )


def export_bundle(layout: CampaignLayout) -> dict[str, Any]:
    def operation() -> dict[str, Any]:
        result = scientific_pipeline.export_bundle(layout.campaign_id)
        return _seal_result(layout, dict(result))

    return _stage(layout, "export_bundle", operation)


def _complete_status(layout: CampaignLayout) -> dict[str, Any]:
    matrix_path = layout.campaign_root / "job_plan.json"
    status = campaign_status(
        layout.campaign_id,
        layout.campaign_root.parent,
        matrix_path=matrix_path if matrix_path.exists() else None,
    )
    total = int(status.get("total") or 0)
    completed = int(status.get("completed_jobs") or 0)
    if total <= 0 or completed != total:
        raise RuntimeError(f"campaign is incomplete: {status}")
    return status


def finalize_campaign(layout: CampaignLayout) -> dict[str, Any]:
    def operation() -> dict[str, Any]:
        status = _complete_status(layout)
        aggregation = scientific_pipeline.aggregate_campaign(layout.campaign_id)
        verification = scientific_pipeline.verify_campaign(layout.campaign_id)
        if not bool(verification.get("verified")):
            raise RuntimeError(f"campaign verification failed: {verification}")
        rendering = scientific_pipeline.render_campaign(layout.campaign_id)
        release = _seal_result(
            layout,
            dict(scientific_pipeline.export_bundle(layout.campaign_id)),
        )
        bundle_dir = Path(str(release["bundle_dir"]))

        layout.finalized_dir.mkdir(parents=True, exist_ok=True)
        archive_base = layout.finalized_dir / f"{layout.campaign_id}-bundle"
        archive = Path(
            shutil.make_archive(str(archive_base), "zip", root_dir=bundle_dir)
        )
        archive_hash = _file_hash(archive)
        archive_sidecar = archive.with_suffix(archive.suffix + ".sha256")
        archive_sidecar.write_text(
            f"{archive_hash}  {archive.name}\n", encoding="utf-8"
        )
        if _file_hash(archive) != archive_hash:
            raise RuntimeError(f"finalized archive changed after hashing: {archive}")

        return {
            "campaign_id": layout.campaign_id,
            "status": status,
            "aggregation": aggregation,
            "verification": verification,
            "rendering": rendering,
            "release": release,
            "archive": str(archive),
            "archive_sha256": archive_hash,
            "archive_sidecar": str(archive_sidecar),
        }

    return _stage(layout, "finalize", operation)


def verify_run(layout: CampaignLayout) -> dict[str, Any]:
    def operation() -> dict[str, Any]:
        status = _complete_status(layout)
        verification = scientific_pipeline.verify_campaign(layout.campaign_id)
        if not bool(verification.get("verified")):
            raise RuntimeError(f"campaign verification failed: {verification}")

        bundle = layout.bundles_dir / f"{layout.campaign_id}-bundle"
        if not bundle.is_dir():
            raise FileNotFoundError(f"finalized bundle is missing: {bundle}")
        bundle_verification = scientific_pipeline.verify_bundle(bundle)
        if not bool(bundle_verification.get("verified")):
            raise RuntimeError(
                f"bundle verification failed: {bundle_verification}"
            )

        return {
            "campaign_id": layout.campaign_id,
            "status": status,
            "verification": verification,
            "bundles": [bundle_verification],
            "verified": True,
        }

    return _stage(layout, "echo_verify_run", operation)
