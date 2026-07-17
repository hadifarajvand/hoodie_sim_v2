from __future__ import annotations

import csv
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Any, Iterable


PROTECTED_CAMPAIGN_ID = "figures-8-11-7587c7c6382c"


def repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def source_commit() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=repository_root(),
        text=True,
    ).strip()


def resolve_campaign_root(run_root: str | Path, campaign_id: str) -> Path:
    root = Path(run_root).expanduser()
    if not root.is_absolute():
        raise ValueError("--run-root must be absolute")
    root = root.resolve(strict=False)
    repo = repository_root().resolve()
    if root == repo or repo in root.parents:
        raise ValueError("--run-root must be outside the Git repository")
    if not campaign_id or campaign_id in {".", ".."}:
        raise ValueError("--campaign-id must be non-empty")
    if "/" in campaign_id or "\\" in campaign_id:
        raise ValueError("--campaign-id must be one path component")
    if campaign_id == PROTECTED_CAMPAIGN_ID:
        raise ValueError("the protected legacy campaign cannot be mutated")
    campaign = root / "campaigns" / campaign_id
    if PROTECTED_CAMPAIGN_ID in campaign.parts:
        raise ValueError("the protected legacy campaign cannot be mutated")
    return campaign


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
        + "\n"
    ).encode("utf-8")


def atomic_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def atomic_json(path: Path, value: Any) -> str:
    payload = canonical_json(value)
    atomic_bytes(path, payload)
    return sha256(payload).hexdigest()


def atomic_text(path: Path, value: str) -> str:
    payload = value.encode("utf-8")
    atomic_bytes(path, payload)
    return sha256(payload).hexdigest()


def atomic_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> str:
    payload = b"".join(canonical_json(row) for row in rows)
    atomic_bytes(path, payload)
    return sha256(payload).hexdigest()


def atomic_csv(path: Path, rows: list[dict[str, Any]]) -> str:
    buffer = io.StringIO(newline="")
    if rows:
        fieldnames = list(rows[0])
        writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    payload = buffer.getvalue().encode("utf-8")
    atomic_bytes(path, payload)
    return sha256(payload).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tree_hashes(root: Path, *, exclude: set[str] | None = None) -> dict[str, str]:
    excluded = exclude or set()
    return {
        str(path.relative_to(root)): file_sha256(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and str(path.relative_to(root)) not in excluded
        and not path.name.endswith(".tmp")
    }


def write_sha256sums(root: Path, *, output_name: str = "SHA256SUMS") -> Path:
    hashes = tree_hashes(root, exclude={output_name})
    payload = "".join(f"{digest}  {path}\n" for path, digest in hashes.items())
    output = root / output_name
    atomic_text(output, payload)
    return output


def completion_payload(unit_dir: Path) -> dict[str, Any] | None:
    marker = unit_dir / "COMPLETED.json"
    if not marker.is_file():
        return None
    payload = read_json(marker)
    if payload.get("status") != "completed":
        return None
    return payload
