#!/usr/bin/env python3
"""Inventory and validate every file visible to the repository.

The command is intentionally read-only except for its optional report output.
It never deletes, moves, or rewrites project files.
"""

from __future__ import annotations

import argparse
import ast
import csv
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import mimetypes
from pathlib import Path
import re
import subprocess
import sys
from typing import Iterable


FORBIDDEN_TRACKED_PREFIXES = (
    ".claude/",
    ".claude-flow/",
    ".opencode/",
    ".swarm/",
    "runs/",
    "worker-state/",
    "checkpoints/",
    "checkpoint_store/",
    "replay_snapshots/",
    "artifacts/hoodie/campaigns/",
    "artifacts/hoodie/distributed/",
    "artifacts/hoodie/releases/",
    "artifacts/hoodie/runtime/",
    "artifacts/hoodie/worker-state/",
    "artifacts/hoodie/checkpoint_store/",
)
FORBIDDEN_TRACKED_EXACT = {".mcp.json"}
FORBIDDEN_TRACKED_SUFFIXES = (
    ".pid",
    ".sock",
    ".pt",
    ".pth",
    ".ckpt",
    ".safetensors",
)
TEMPORARY_NAMES = {
    "temp_head.txt",
    "temp_middle.txt",
    "audit-request.txt",
}
CRITICAL_TOP_LEVEL_FUNCTIONS = {
    "_validate_bundle",
    "run_shard",
    "import_shard_results",
    "finalize_campaign",
}
MACHINE_LOCAL_PATTERN = re.compile(r"(?:/Users/[^/]+/|/home/[^/]+/|[A-Za-z]:\\\\Users\\\\)")


@dataclass(frozen=True, slots=True)
class FileRecord:
    path: str
    size_bytes: int
    sha256: str
    state: str
    mime_type: str
    last_commit: str | None
    category: str
    proposed_action: str
    deletion_safety: str
    active_reference_count: int


def run_git(root: Path, *args: str, check: bool = True) -> bytes:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout


def repo_root() -> Path:
    completed = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return Path(completed.stdout.strip()).resolve()


def nul_paths(payload: bytes) -> list[str]:
    return [part.decode("utf-8", errors="surrogateescape") for part in payload.split(b"\0") if part]


def file_hash(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def classify(path: str) -> tuple[str, str, str]:
    lower = path.lower()
    name = Path(path).name

    if path.startswith(("src/", "hoodie/")) and path.endswith((".py", ".pyi")):
        return "core source", "keep", "not removable"
    if path.startswith(("tests/", "tests_supported/")):
        return "active test", "keep", "not removable"
    if path.startswith("tests_historical/"):
        return "historical evidence", "archive outside active test discovery", "manual review"
    if path.startswith(("configs/", ".github/")) or name in {
        "pyproject.toml",
        "requirements.txt",
        ".gitignore",
        "AGENTS.md",
    }:
        return "active configuration", "keep", "not removable"
    if path.startswith("resources/papers/hoodie/"):
        return "approved scientific reference", "keep", "not removable"
    if path.startswith("resources/"):
        return "approved scientific reference", "review vendored scope", "manual review"
    if path.startswith(("docs/", "specs/")) or path.endswith(".md"):
        return "required documentation", "keep or archive by current relevance", "manual review"
    if path.startswith("archive/"):
        return "historical evidence", "keep indexed or move to release storage", "manual review"
    if path.startswith(("artifacts/analysis/", "artifacts/control/", "artifacts/reports/")):
        return "historical evidence", "move to archive or external release storage", "safe after hash/index verification"
    if path.startswith("artifacts/hoodie/"):
        return "generated experiment output", "untrack and store under HOODIE_RUN_ROOT", "safe after reference verification"
    if path.startswith((".claude/", ".claude-flow/", ".opencode/", ".swarm/")) or path == ".mcp.json":
        return "runtime state", "remove from Git", "safe after external-tool confirmation"
    if name in TEMPORARY_NAMES or lower.endswith((".part", ".transport", ".payload")):
        return "temporary transport", "remove after checksum verification", "safe after hash/index verification"
    if lower.endswith((".log", ".pid", ".sock", ".pt", ".pth", ".ckpt", ".safetensors", ".jsonl")):
        return "runtime state", "untrack and store externally", "safe after scientific-reference verification"
    if path.startswith("scripts/"):
        return "core source", "keep", "not removable"
    if path.startswith((".git/", ".venv/", "venv/", "__pycache__/")):
        return "runtime state", "ignore", "safe"
    if path.endswith((".py", ".toml", ".yaml", ".yml", ".json")):
        return "active configuration", "review and keep if referenced", "manual review"
    return "unknown/manual review", "classify manually", "unsafe"


def last_commit(root: Path, path: str, tracked: bool) -> str | None:
    if not tracked:
        return None
    output = run_git(root, "log", "-1", "--format=%H", "--", path, check=False).decode().strip()
    return output or None


def reference_count(root: Path, path: str, tracked_text: list[Path]) -> int:
    # A deterministic conservative approximation: count exact repository-relative
    # path mentions. This avoids interpreting generated binary data as text.
    needle = path.encode("utf-8")
    count = 0
    for candidate in tracked_text:
        try:
            if candidate == root / path:
                continue
            data = candidate.read_bytes()
        except (OSError, ValueError):
            continue
        count += data.count(needle)
    return count


def python_duplicate_issues(root: Path, tracked: Iterable[str]) -> list[dict[str, object]]:
    issues: list[dict[str, object]] = []
    for relative in tracked:
        if not relative.endswith(".py"):
            continue
        path = root / relative
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        except (OSError, UnicodeDecodeError, SyntaxError) as exc:
            issues.append({"path": relative, "issue": "python_parse_failed", "detail": str(exc)})
            continue
        names: dict[str, int] = {}
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                names[node.name] = names.get(node.name, 0) + 1
        for name, count in names.items():
            if count > 1 and (name in CRITICAL_TOP_LEVEL_FUNCTIONS or not name.startswith("test_")):
                issues.append(
                    {
                        "path": relative,
                        "issue": "duplicate_top_level_function",
                        "function": name,
                        "count": count,
                    }
                )
    return issues


def machine_local_path_issues(root: Path, tracked: Iterable[str]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for relative in tracked:
        path = root / relative
        if path.suffix.lower() not in {".md", ".txt", ".py", ".toml", ".yaml", ".yml", ".json", ".sh"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        match = MACHINE_LOCAL_PATTERN.search(text)
        if match:
            issues.append({"path": relative, "match": match.group(0)})
    return issues


def inventory(root: Path) -> tuple[list[FileRecord], dict[str, object]]:
    tracked = sorted(nul_paths(run_git(root, "ls-files", "-z")))
    untracked = sorted(nul_paths(run_git(root, "ls-files", "--others", "--exclude-standard", "-z")))
    ignored = sorted(nul_paths(run_git(root, "ls-files", "--others", "--ignored", "--exclude-standard", "-z")))

    tracked_set = set(tracked)
    untracked_set = set(untracked)
    ignored_set = set(ignored)
    all_paths = sorted(tracked_set | untracked_set | ignored_set)

    text_candidates = [
        root / relative
        for relative in tracked
        if (root / relative).is_file() and (root / relative).stat().st_size <= 2 * 1024 * 1024
    ]

    records: list[FileRecord] = []
    for relative in all_paths:
        path = root / relative
        if not path.is_file():
            continue
        category, proposed_action, deletion_safety = classify(relative)
        state = "tracked" if relative in tracked_set else "untracked" if relative in untracked_set else "ignored"
        records.append(
            FileRecord(
                path=relative,
                size_bytes=path.stat().st_size,
                sha256=file_hash(path),
                state=state,
                mime_type=mimetypes.guess_type(relative)[0] or "application/octet-stream",
                last_commit=last_commit(root, relative, relative in tracked_set),
                category=category,
                proposed_action=proposed_action,
                deletion_safety=deletion_safety,
                active_reference_count=reference_count(root, relative, text_candidates),
            )
        )

    forbidden_tracked = sorted(
        relative
        for relative in tracked
        if relative in FORBIDDEN_TRACKED_EXACT
        or relative.endswith(FORBIDDEN_TRACKED_SUFFIXES)
        or relative.startswith(FORBIDDEN_TRACKED_PREFIXES)
    )
    unknown_tracked = sorted(record.path for record in records if record.state == "tracked" and record.category == "unknown/manual review")
    duplicate_issues = python_duplicate_issues(root, tracked)
    machine_paths = machine_local_path_issues(root, tracked)

    summary: dict[str, object] = {
        "repository_root": str(root),
        "head": run_git(root, "rev-parse", "HEAD").decode().strip(),
        "branch": run_git(root, "branch", "--show-current").decode().strip(),
        "tracked_files": len(tracked),
        "untracked_files": len(untracked),
        "ignored_files": len(ignored),
        "inventoried_files": len(records),
        "tracked_bytes": sum(record.size_bytes for record in records if record.state == "tracked"),
        "forbidden_tracked_paths": forbidden_tracked,
        "unknown_tracked_paths": unknown_tracked,
        "duplicate_python_definitions": duplicate_issues,
        "machine_local_paths": machine_paths,
        "passed": not forbidden_tracked and not unknown_tracked and not duplicate_issues and not machine_paths,
    }
    return records, summary


def write_reports(output_dir: Path, records: list[FileRecord], summary: dict[str, object]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "repository_inventory.json").write_text(
        json.dumps({"summary": summary, "files": [asdict(record) for record in records]}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    with (output_dir / "repository_inventory.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(records[0]).keys()) if records else ["path"])
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))
    (output_dir / "repository_audit_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="return non-zero when repository policy fails")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="optional report directory; defaults to $HOODIE_RUN_ROOT/audits/repository when set",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()
    records, summary = inventory(root)

    output_dir = args.output_dir
    if output_dir is None:
        import os

        run_root = os.environ.get("HOODIE_RUN_ROOT")
        if run_root:
            output_dir = Path(run_root).expanduser().resolve() / "audits" / "repository"
    if output_dir is not None:
        write_reports(output_dir, records, summary)

    print(json.dumps(summary, sort_keys=True))
    return 1 if args.check and not bool(summary["passed"]) else 0


if __name__ == "__main__":
    sys.exit(main())
