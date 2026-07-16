from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

import torch


_INSTALLED = False


def _file_hash(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def register_training_checkpoint(
    job_dir: Path,
    row: Any,
    *,
    source_commit: str,
    checkpoint_id: str,
) -> dict[str, Any]:
    from . import production_campaign as production

    checkpoint_dir = production._job_internal_checkpoint_dir(job_dir) / checkpoint_id
    checkpoint_path = checkpoint_dir / "checkpoint.pt"
    if not checkpoint_path.is_file():
        raise FileNotFoundError(checkpoint_path)
    checkpoint_state = torch.load(
        checkpoint_path, map_location="cpu", weights_only=False
    )
    if not isinstance(checkpoint_state, dict):
        raise ValueError("selected checkpoint must contain a dictionary")
    metadata_path = checkpoint_dir / "metadata.json"
    metadata = (
        json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata_path.is_file()
        else {}
    )
    checkpoint_hash = _file_hash(checkpoint_path)
    metadata_hash = str(metadata.get("checkpoint_sha256", ""))
    if metadata_hash and metadata_hash != checkpoint_hash:
        raise ValueError("checkpoint metadata SHA-256 mismatch")

    campaign_dir = job_dir.parent.parent
    registry = production._load_campaign_checkpoint_registry(campaign_dir)
    record = {
        "training_job_id": row.job_id,
        "checkpoint_id": checkpoint_id,
        "checkpoint_path": str(checkpoint_path),
        "checkpoint_hash": checkpoint_hash,
        "checkpoint_size_bytes": checkpoint_path.stat().st_size,
        "policy": row.policy,
        "variant": row.variant,
        "seed": int(row.seed or 0),
        "backend_type": str(checkpoint_state.get("backend_type", "legacy_unknown")),
        "device_string": str(checkpoint_state.get("device_string", "")),
        "source_commit": source_commit,
        "source_contract_hash": row.source_contract_hash,
        "job_spec_hash": production._hash(asdict(row)),
        "checkpoint_schema_version": int(
            checkpoint_state.get("schema_version", 0)
        ),
        "resume_capable": bool(checkpoint_state.get("resume_capable", False)),
        "scientifically_complete": True,
    }
    registry = [
        item
        for item in registry
        if item.get("training_job_id") != row.job_id
    ]
    registry.append(record)
    production._write_campaign_checkpoint_registry(campaign_dir, registry)
    production._write_json(job_dir / "selected_checkpoint.json", record)
    return record


def install_checkpoint_registry_patch() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    from . import production_campaign

    production_campaign._register_training_checkpoint = register_training_checkpoint
    _INSTALLED = True
