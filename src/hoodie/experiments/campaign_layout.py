from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping


PROTECTED_CAMPAIGN_IDS = frozenset({"figures-8-11-7587c7c6382c"})


class CampaignLocationError(ValueError):
    """Raised when campaign location arguments are invalid or ambiguous."""


class CampaignNotFoundError(FileNotFoundError):
    """Raised when an explicitly selected campaign does not exist."""

    error_type = "campaign_not_found"


@dataclass(frozen=True, slots=True)
class CampaignLayout:
    repository_root: Path
    campaign_root: Path
    manifest_path: Path
    jobs_dir: Path
    checkpoints_dir: Path
    traces_dir: Path
    logs_dir: Path
    aggregate_dir: Path
    verification_dir: Path
    figures_dir: Path
    bundle_staging_dir: Path
    bundles_dir: Path
    finalized_dir: Path
    sha256sums_path: Path

    @property
    def campaign_id(self) -> str:
        return self.campaign_root.name

    def as_dict(self) -> dict[str, str]:
        return {
            "repository_root": str(self.repository_root),
            "campaign_root": str(self.campaign_root),
            "manifest_path": str(self.manifest_path),
            "jobs_dir": str(self.jobs_dir),
            "checkpoints_dir": str(self.checkpoints_dir),
            "traces_dir": str(self.traces_dir),
            "logs_dir": str(self.logs_dir),
            "aggregate_dir": str(self.aggregate_dir),
            "verification_dir": str(self.verification_dir),
            "figures_dir": str(self.figures_dir),
            "bundle_staging_dir": str(self.bundle_staging_dir),
            "bundles_dir": str(self.bundles_dir),
            "finalized_dir": str(self.finalized_dir),
            "sha256sums_path": str(self.sha256sums_path),
        }


def repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _normalize(path: str | os.PathLike[str] | Path) -> Path:
    return Path(path).expanduser().resolve(strict=False)


def _require_absolute(
    value: str | os.PathLike[str] | Path, option: str
) -> Path:
    raw = Path(value).expanduser()
    if not raw.is_absolute():
        raise CampaignLocationError(f"{option} must be an absolute path: {value}")
    return _normalize(raw)


def _inside(path: Path, parent: Path) -> bool:
    return path == parent or parent in path.parents


def _validate_campaign_id(campaign_id: str) -> str:
    value = str(campaign_id).strip()
    if not value:
        raise CampaignLocationError("campaign_id must not be empty")
    if value in {".", ".."} or "/" in value or "\\" in value:
        raise CampaignLocationError("campaign_id must be a single path component")
    if value in PROTECTED_CAMPAIGN_IDS:
        raise CampaignLocationError(f"protected legacy campaign is not accessible: {value}")
    return value


def _campaign_from_run_root(run_root: Path, campaign_id: str) -> Path:
    # Accept either the external application root (.../echo_outputs) or its
    # explicit campaigns directory (.../echo_outputs/campaigns).
    base = run_root if run_root.name == "campaigns" else run_root / "campaigns"
    return base / campaign_id


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CampaignNotFoundError(str(path)) from exc
    if not isinstance(payload, dict):
        raise CampaignLocationError(f"manifest must contain a JSON object: {path}")
    return payload


def resolve_campaign_layout(
    *,
    campaign_dir: str | os.PathLike[str] | Path | None = None,
    manifest_path: str | os.PathLike[str] | Path | None = None,
    run_root: str | os.PathLike[str] | Path | None = None,
    campaign_id: str | None = None,
    repository: str | os.PathLike[str] | Path | None = None,
    require_existing: bool = True,
) -> CampaignLayout:
    repo = _normalize(repository or repository_root())

    selectors = int(campaign_dir is not None) + int(manifest_path is not None)
    if selectors > 1:
        raise CampaignLocationError(
            "choose exactly one campaign selector: --campaign-dir or --manifest"
        )
    if campaign_dir is not None and (run_root is not None or campaign_id is not None):
        raise CampaignLocationError(
            "--campaign-dir cannot be combined with --run-root or --campaign-id"
        )
    if manifest_path is not None and (run_root is not None or campaign_id is not None):
        raise CampaignLocationError(
            "--manifest cannot be combined with --run-root or --campaign-id"
        )

    resolved_manifest_path: Path | None = None

    if campaign_dir is not None:
        root = _require_absolute(campaign_dir, "--campaign-dir")
        selected_id = _validate_campaign_id(root.name)
    elif manifest_path is not None:
        selected_manifest = _require_absolute(manifest_path, "--manifest")
        manifest = _read_json(selected_manifest)
        resolved_manifest_path = selected_manifest
        raw_root = manifest.get("campaign_root")
        if not raw_root:
            raise CampaignLocationError(
                f"manifest does not record campaign_root: {selected_manifest}"
            )
        root = _normalize(str(raw_root))
        selected_id = _validate_campaign_id(str(manifest.get("campaign_id") or root.name))
        if root.name != selected_id:
            raise CampaignLocationError(
                "manifest campaign_id does not match campaign_root basename"
            )
    else:
        if campaign_id is None:
            raise CampaignLocationError(
                "campaign location required: use --campaign-dir, --manifest, "
                "or --run-root with --campaign-id"
            )
        selected_id = _validate_campaign_id(campaign_id)
        raw_run_root = run_root or os.environ.get("ECHO_RUN_ROOT") or os.environ.get(
            "HOODIE_RUN_ROOT"
        )
        if raw_run_root is None:
            raise CampaignLocationError(
                "--run-root is required when campaign_id is supplied"
            )
        normalized_run_root = _require_absolute(raw_run_root, "--run-root")
        root = _normalize(_campaign_from_run_root(normalized_run_root, selected_id))

    if _inside(root, repo):
        raise CampaignLocationError(
            f"campaign root must be outside the repository: {root}"
        )
    if root.name in PROTECTED_CAMPAIGN_IDS:
        raise CampaignLocationError(
            f"protected legacy campaign is not accessible: {root.name}"
        )

    if require_existing and not root.is_dir():
        raise CampaignNotFoundError(str(root))

    canonical_manifest = resolved_manifest_path or (root / "campaign_manifest.json")
    return CampaignLayout(
        repository_root=repo,
        campaign_root=root,
        manifest_path=canonical_manifest,
        jobs_dir=root / "jobs",
        checkpoints_dir=root / "checkpoints",
        traces_dir=root / "traces",
        logs_dir=root / "logs",
        aggregate_dir=root / "aggregates",
        verification_dir=root / "verification",
        figures_dir=root / "figures",
        bundle_staging_dir=root.parent / "bundle-staging" / selected_id,
        bundles_dir=root.parent / "releases",
        finalized_dir=root.parent / "finalized" / selected_id,
        sha256sums_path=root.parent / "finalized" / selected_id / "SHA256SUMS",
    )


def load_campaign_manifest(layout: CampaignLayout) -> dict[str, Any]:
    if layout.manifest_path.exists():
        payload = _read_json(layout.manifest_path)
    else:
        payload = {}
    payload.setdefault("campaign_id", layout.campaign_id)
    payload.setdefault("campaign_root", str(layout.campaign_root))
    return payload


def atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(dict(payload), indent=2, sort_keys=True, default=str) + "\n"
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def record_stage(
    layout: CampaignLayout,
    stage: str,
    *,
    status: str,
    details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    manifest = load_campaign_manifest(layout)
    manifest["campaign_id"] = layout.campaign_id
    manifest["campaign_root"] = str(layout.campaign_root)
    stages = manifest.setdefault("stages", {})
    if not isinstance(stages, dict):
        stages = {}
        manifest["stages"] = stages
    stages[stage] = {
        "status": status,
        **(dict(details) if details else {}),
    }
    atomic_write_json(layout.manifest_path, manifest)
    return manifest
