#!/usr/bin/env python3
"""Validate a user-selected HOODIE runtime/output root safely.

The validator is intentionally standalone so Claude Code can run it before the
package is installed. It never removes user data. The only files it deletes are
small probe files that it created itself during the current invocation.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import secrets
import shlex
import shutil
import subprocess
import sys
import tempfile
from typing import Any

GIB = 1024**3


def repository_root() -> Path:
    completed = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return Path(completed.stdout.strip()).resolve()


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    descriptor = os.open(path, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write_and_atomic_replace_probe(root: Path) -> dict[str, Any]:
    payload = secrets.token_bytes(4096)
    expected_hash = sha256(payload).hexdigest()
    temporary: Path | None = None
    promoted = root / f".hoodie-root-probe-promoted-{os.getpid()}"

    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=root,
            prefix=".hoodie-root-probe-",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())

        observed_hash = sha256(temporary.read_bytes()).hexdigest()
        if observed_hash != expected_hash:
            raise OSError("write/read integrity probe failed")

        os.replace(temporary, promoted)
        temporary = None
        _fsync_directory(root)

        promoted_hash = sha256(promoted.read_bytes()).hexdigest()
        if promoted_hash != expected_hash:
            raise OSError("atomic-replace integrity probe failed")

        return {
            "write_probe_bytes": len(payload),
            "write_probe_sha256": expected_hash,
            "write_read_verified": True,
            "atomic_replace_verified": True,
        }
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        promoted.unlink(missing_ok=True)


def validate_run_root(
    candidate: str,
    *,
    minimum_free_gib: int = 20,
    minimum_free_fraction: float = 0.10,
    create: bool = True,
) -> dict[str, Any]:
    repo = repository_root()
    expanded = Path(candidate).expanduser()

    errors: list[str] = []
    if not expanded.is_absolute():
        errors.append("path must be absolute (a leading ~ is accepted)")
        root = expanded.absolute().resolve(strict=False)
    else:
        root = expanded.resolve(strict=False)

    if root == repo or repo in root.parents:
        errors.append("run root must be outside the Git repository")

    if root.exists() and not root.is_dir():
        errors.append("selected path exists but is not a directory")

    if minimum_free_gib < 1:
        errors.append("minimum_free_gib must be at least 1")
    if not 0.0 < minimum_free_fraction < 1.0:
        errors.append("minimum_free_fraction must be in (0, 1)")

    if errors:
        return {
            "passed": False,
            "candidate": candidate,
            "resolved_path": str(root),
            "repository_root": str(repo),
            "errors": errors,
        }

    if create:
        root.mkdir(parents=True, exist_ok=True)
    elif not root.is_dir():
        return {
            "passed": False,
            "candidate": candidate,
            "resolved_path": str(root),
            "repository_root": str(repo),
            "errors": ["selected directory does not exist"],
        }

    usage = shutil.disk_usage(root)
    required_free_bytes = max(
        minimum_free_gib * GIB,
        int(usage.total * minimum_free_fraction),
    )

    if usage.free < required_free_bytes:
        errors.append(
            "insufficient free space: "
            f"free={usage.free}, required={required_free_bytes}"
        )

    if not os.access(root, os.W_OK | os.X_OK):
        errors.append("selected directory is not writable/searchable")

    probe: dict[str, Any] = {
        "write_read_verified": False,
        "atomic_replace_verified": False,
    }
    if not errors:
        try:
            probe = _write_and_atomic_replace_probe(root)
        except Exception as exc:  # concise fail-closed diagnostic
            errors.append(f"filesystem probe failed: {type(exc).__name__}: {exc}")

    stat_result = root.stat()
    payload: dict[str, Any] = {
        "passed": not errors,
        "candidate": candidate,
        "resolved_path": str(root),
        "repository_root": str(repo),
        "outside_repository": root != repo and repo not in root.parents,
        "directory_exists": root.is_dir(),
        "writable": os.access(root, os.W_OK | os.X_OK),
        "filesystem_device_id": stat_result.st_dev,
        "free_bytes": usage.free,
        "total_bytes": usage.total,
        "used_bytes": usage.used,
        "minimum_free_gib": minimum_free_gib,
        "minimum_free_fraction": minimum_free_fraction,
        "required_free_bytes": required_free_bytes,
        **probe,
        "errors": errors,
    }
    return payload


def _write_env_file(path: Path, resolved_root: str) -> None:
    path = path.expanduser().resolve(strict=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = f"export HOODIE_RUN_ROOT={shlex.quote(resolved_root)}\n"
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
        _fsync_directory(path.parent)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True, help="user-selected output root")
    parser.add_argument("--minimum-free-gib", type=int, default=20)
    parser.add_argument("--minimum-free-fraction", type=float, default=0.10)
    parser.add_argument(
        "--no-create",
        action="store_true",
        help="require the selected directory to exist instead of creating it",
    )
    parser.add_argument(
        "--write-env-file",
        type=Path,
        default=None,
        help="after a successful check, atomically write a sourceable env file",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = validate_run_root(
        args.path,
        minimum_free_gib=args.minimum_free_gib,
        minimum_free_fraction=args.minimum_free_fraction,
        create=not args.no_create,
    )

    if result["passed"] and args.write_env_file is not None:
        _write_env_file(args.write_env_file, str(result["resolved_path"]))
        result["env_file"] = str(args.write_env_file.expanduser().resolve())

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
