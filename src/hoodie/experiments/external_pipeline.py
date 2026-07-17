from __future__ import annotations

from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
import shutil
import time
from typing import Any, Iterator

from .campaign import campaign_status
from .campaign_layout import CampaignLayout, record_stage
from . import distributed_v2
from . import scientific_pipeline


def _file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _write_sha256sums(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    entries: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name == "SHA256SUMS":
            continue
        entries.append(f"{_file_hash(path)}  {path.relative_to(root)}")
    output = root / "SHA256SUMS"
    output.write_text("\n".join(entries) + ("\n" if entries else ""), encoding="utf-8")
    return output


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
    record_stage(
        layout,
        name,
        status="running",
        details={"started_at": started, "campaign_root": str(layout.campaign_root)},
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
        bundle_dir = Path(str(result["bundle_dir"])).resolve()
        checksum_path = _write_sha256sums(bundle_dir)
        return {
            **result,
            "bundle_dir": str(bundle_dir),
            "sha256sums": str(checksum_path),
        }

    return _stage(layout, "export_bundle", operation)


def finalize_campaign(layout: CampaignLayout) -> dict[str, Any]:
    def operation() -> dict[str, Any]:
        matrix_path = layout.campaign_root / "job_plan.json"
        status = campaign_status(
            layout.campaign_id,
            layout.campaign_root.parent,
            matrix_path=matrix_path if matrix_path.exists() else None,
        )
        if status.get("completed_jobs") != status.get("total"):
            raise RuntimeError(f"campaign is incomplete and cannot be finalized: {status}")

        aggregation = scientific_pipeline.aggregate_campaign(layout.campaign_id)
        verification = scientific_pipeline.verify_campaign(layout.campaign_id)
        rendering = scientific_pipeline.render_campaign(layout.campaign_id)
        release = scientific_pipeline.export_bundle(layout.campaign_id)
        bundle_dir = Path(str(release["bundle_dir"])).resolve()
        checksum_path = _write_sha256sums(bundle_dir)

        layout.finalized_dir.mkdir(parents=True, exist_ok=True)
        archive_base = layout.finalized_dir / f"{layout.campaign_id}-bundle"
        archive = Path(shutil.make_archive(str(archive_base), "zip", root_dir=bundle_dir))
        archive_sidecar = archive.with_suffix(archive.suffix + ".sha256")
        archive_sidecar.write_text(
            f"{_file_hash(archive)}  {archive.name}\n", encoding="utf-8"
        )

        return {
            "campaign_id": layout.campaign_id,
            "status": status,
            "aggregation": aggregation,
            "verification": verification,
            "rendering": rendering,
            "release": {
                **release,
                "bundle_dir": str(bundle_dir),
                "sha256sums": str(checksum_path),
            },
            "archive": str(archive),
            "archive_sha256": _file_hash(archive),
            "archive_sidecar": str(archive_sidecar),
        }

    return _stage(layout, "finalize", operation)


def verify_run(layout: CampaignLayout) -> dict[str, Any]:
    matrix_path = layout.campaign_root / "job_plan.json"
    status = campaign_status(
        layout.campaign_id,
        layout.campaign_root.parent,
        matrix_path=matrix_path if matrix_path.exists() else None,
    )
    if status.get("completed_jobs") != status.get("total"):
        raise RuntimeError(f"campaign is incomplete: {status}")

    verification = verify_campaign(layout)
    bundle_candidates = sorted(
        path
        for path in layout.bundles_dir.glob(f"{layout.campaign_id}-bundle*")
        if path.is_dir()
    )
    bundle_verifications: list[dict[str, Any]] = []
    for bundle in bundle_candidates:
        bundle_verifications.append(scientific_pipeline.verify_bundle(bundle))

    payload = {
        "campaign_id": layout.campaign_id,
        "campaign_root": str(layout.campaign_root),
        "status": status,
        "verification": verification,
        "bundles": bundle_verifications,
        "verified": bool(verification.get("verified")),
    }
    record_stage(layout, "echo_verify_run", status="completed", details=payload)
    return payload
