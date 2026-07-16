#!/usr/bin/env python3
"""Inventory every tracked and untracked repository file and enforce policy.

The audit is read-only except for its optional report directory. Ignored files
are counted but never opened or hashed, so an old checkpoint tree or virtual
environment cannot make the audit consume the disk or memory it is meant to
protect.
"""

from __future__ import annotations

import argparse
import ast
import csv
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import mimetypes
import os
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
    "verify_campaign",
}
MACHINE_LOCAL_PATTERN = re.compile(
    r"(?:/Users/[^/]+/|/home/[^/]+/|[A-Za-z]:\\Users\\)"
)
PATH_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_.@+-]+(?:/[A-Za-z0-9_.@+ -]+)+")
ACTIVE_PORTABILITY_PREFIXES = (
    "src/",
    "hoodie/",
    "scripts/",
    "configs/",
    ".github/",
    "docs/architecture/",
    "docs/runbooks/",
)
ACTIVE_PORTABILITY_EXACT = {
    "README.md",
    "AGENTS.md",
    "pyproject.toml",
    "requirements.txt",
}


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
    return [
        part.decode("utf-8", errors="surrogateescape")
        for part in payload.split(b"\0")
        if part
    ]


def file_hash(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def classify(path: str) -> tuple[str, str, str]:
    lower = path.lower()
    name = Path(path).name
    suffix = Path(path).suffix.lower()

    if path.startswith(("src/", "hoodie/")) and suffix in {
        ".py",
        ".pyi",
        ".json",
        ".yaml",
        ".yml",
    }:
        return "core source", "keep", "not removable"
    if path.startswith(("tests/", "tests_supported/")):
        return "active test", "keep", "not removable"
    if path.startswith("tests_historical/"):
        return (
            "historical evidence",
            "archive outside active test discovery",
            "manual review",
        )
    if path.startswith(("configs/", ".github/")) or name in {
        "pyproject.toml",
        "requirements.txt",
        "requirements-dev.txt",
        ".gitignore",
        ".gitattributes",
        ".editorconfig",
        "AGENTS.md",
        "Dockerfile",
        "Makefile",
        "package.json",
        "package-lock.json",
        "uv.lock",
        "tox.ini",
        "pytest.ini",
    }:
        return "active configuration", "keep", "not removable"
    if path.startswith(("resources/papers/hoodie/", "references/")):
        return "approved scientific reference", "keep", "not removable"
    if path.startswith("resources/"):
        return (
            "approved scientific reference",
            "review vendored scope",
            "manual review",
        )
    if path.startswith(("docs/", "specs/", "notebooks/", "assets/")) or suffix in {
        ".md",
        ".rst",
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
        ".svg",
        ".gif",
    }:
        return (
            "required documentation",
            "keep or archive by current relevance",
            "manual review",
        )
    if path.startswith("archive/"):
        return (
            "historical evidence",
            "keep indexed or move to release storage",
            "manual review",
        )
    if path.startswith(
        (
            "artifacts/analysis/",
            "artifacts/control/",
            "artifacts/reports/",
            "artifacts/smoke/",
            "artifacts/test_triage/",
            "artifacts/reconciliation/",
        )
    ):
        return (
            "historical evidence",
            "move to archive or external release storage",
            "safe after hash/index verification",
        )
    if path.startswith("artifacts/hoodie/source_contracts/"):
        return (
            "approved scientific reference",
            "migrate to resources/papers/hoodie/contracts when references permit",
            "manual review",
        )
    if path.startswith("artifacts/hoodie/"):
        return (
            "generated experiment output",
            "untrack and store under HOODIE_RUN_ROOT",
            "safe after reference verification",
        )
    if path.startswith("artifacts/"):
        return (
            "historical evidence",
            "archive or move to external release storage",
            "safe after hash/index verification",
        )
    if path.startswith(
        (".claude/", ".claude-flow/", ".opencode/", ".swarm/")
    ) or path == ".mcp.json":
        return (
            "runtime state",
            "remove from Git",
            "safe after external-tool confirmation",
        )
    if name in TEMPORARY_NAMES or lower.endswith(
        (".part", ".transport", ".payload")
    ):
        return (
            "temporary transport",
            "remove after checksum verification",
            "safe after hash/index verification",
        )
    if lower.endswith(
        (
            ".log",
            ".pid",
            ".sock",
            ".pt",
            ".pth",
            ".ckpt",
            ".safetensors",
            ".jsonl",
        )
    ):
        return (
            "runtime state",
            "untrack and store externally",
            "safe after scientific-reference verification",
        )
    if path.startswith("scripts/") or suffix in {
        ".py",
        ".sh",
        ".js",
        ".cjs",
        ".mjs",
        ".ts",
    }:
        return "core source", "keep", "not removable"
    if suffix in {
        ".toml",
        ".yaml",
        ".yml",
        ".json",
        ".ini",
        ".cfg",
        ".lock",
        ".conf",
    }:
        return (
            "active configuration",
            "review and keep if referenced",
            "manual review",
        )
    if suffix in {".csv", ".tsv", ".xml", ".html", ".parquet"}:
        return (
            "historical evidence",
            "review data provenance and archive",
            "manual review",
        )
    if name in {"LICENSE", "NOTICE", "CITATION.cff", "CODEOWNERS"}:
        return "required documentation", "keep", "not removable"
    return "unknown/manual review", "classify manually", "unsafe"


def last_commit_map(root: Path, tracked: set[str]) -> dict[str, str]:
    """Resolve the most recent commit touching each tracked path in one walk."""

    output = run_git(root, "log", "--format=%x1e%H", "--name-only", check=False)
    current: str | None = None
    result: dict[str, str] = {}
    # Do not use splitlines(): Python treats the record separator as a line
    # boundary and would discard the marker used to identify commits.
    for raw_line in output.decode("utf-8", errors="replace").split("\n"):
        if raw_line.startswith("\x1e"):
            current = raw_line[1:].strip()
            continue
        relative = raw_line.strip()
        if current and relative in tracked and relative not in result:
            result[relative] = current
        if len(result) == len(tracked):
            break
    return result


def reference_counts(root: Path, tracked: list[str]) -> dict[str, int]:
    """Count exact repository-path tokens in tracked text with one bounded scan."""

    known = set(tracked)
    counts = {path: 0 for path in tracked}
    for relative in tracked:
        path = root / relative
        if not path.is_file() or path.stat().st_size > 4 * 1024 * 1024:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for token in PATH_TOKEN_PATTERN.findall(text):
            normalized = token.strip("'\"`()[]{}.,:;")
            if normalized in known and normalized != relative:
                counts[normalized] += 1
    return counts


def python_duplicate_issues(
    root: Path, tracked: Iterable[str]
) -> list[dict[str, object]]:
    issues: list[dict[str, object]] = []
    for relative in tracked:
        if not relative.endswith(".py"):
            continue
        path = root / relative
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        except (OSError, UnicodeDecodeError, SyntaxError) as exc:
            issues.append(
                {"path": relative, "issue": "python_parse_failed", "detail": str(exc)}
            )
            continue
        names: dict[str, int] = {}
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                names[node.name] = names.get(node.name, 0) + 1
        for name, count in names.items():
            if count > 1 and name in CRITICAL_TOP_LEVEL_FUNCTIONS:
                issues.append(
                    {
                        "path": relative,
                        "issue": "duplicate_critical_top_level_function",
                        "function": name,
                        "count": count,
                    }
                )
    return issues


def machine_local_path_issues(
    root: Path, tracked: Iterable[str]
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    all_issues: list[dict[str, str]] = []
    blocking: list[dict[str, str]] = []
    for relative in tracked:
        path = root / relative
        if path.suffix.lower() not in {
            ".md",
            ".txt",
            ".py",
            ".toml",
            ".yaml",
            ".yml",
            ".json",
            ".sh",
        }:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        match = MACHINE_LOCAL_PATTERN.search(text)
        if not match:
            continue
        issue = {"path": relative, "match": match.group(0)}
        all_issues.append(issue)
        if relative in ACTIVE_PORTABILITY_EXACT or relative.startswith(
            ACTIVE_PORTABILITY_PREFIXES
        ):
            blocking.append(issue)
    return all_issues, blocking


def inventory(root: Path) -> tuple[list[FileRecord], dict[str, object]]:
    tracked = sorted(nul_paths(run_git(root, "ls-files", "-z")))
    untracked = sorted(
        nul_paths(run_git(root, "ls-files", "--others", "--exclude-standard", "-z"))
    )
    ignored_payload = run_git(
        root,
        "ls-files",
        "--others",
        "--ignored",
        "--exclude-standard",
        "-z",
    )
    ignored_count = ignored_payload.count(b"\0")

    tracked_set = set(tracked)
    all_paths = sorted(tracked_set | set(untracked))
    commits = last_commit_map(root, tracked_set)
    references = reference_counts(root, tracked)

    records: list[FileRecord] = []
    for relative in all_paths:
        path = root / relative
        if not path.is_file():
            continue
        category, proposed_action, deletion_safety = classify(relative)
        tracked_state = relative in tracked_set
        records.append(
            FileRecord(
                path=relative,
                size_bytes=path.stat().st_size,
                sha256=file_hash(path),
                state="tracked" if tracked_state else "untracked",
                mime_type=mimetypes.guess_type(relative)[0]
                or "application/octet-stream",
                last_commit=commits.get(relative) if tracked_state else None,
                category=category,
                proposed_action=proposed_action,
                deletion_safety=deletion_safety,
                active_reference_count=references.get(relative, 0),
            )
        )

    forbidden_tracked = sorted(
        relative
        for relative in tracked
        if relative in FORBIDDEN_TRACKED_EXACT
        or relative.endswith(FORBIDDEN_TRACKED_SUFFIXES)
        or relative.startswith(FORBIDDEN_TRACKED_PREFIXES)
    )
    unknown_tracked = sorted(
        record.path
        for record in records
        if record.state == "tracked" and record.category == "unknown/manual review"
    )
    duplicate_issues = python_duplicate_issues(root, tracked)
    machine_paths, blocking_machine_paths = machine_local_path_issues(root, tracked)
    dirty_entries = nul_paths(
        run_git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    )
    category_counts: dict[str, int] = {}
    for record in records:
        category_counts[record.category] = category_counts.get(record.category, 0) + 1

    summary: dict[str, object] = {
        "repository_root": str(root),
        "head": run_git(root, "rev-parse", "HEAD").decode().strip(),
        "branch": run_git(root, "branch", "--show-current").decode().strip(),
        "working_tree_clean": not dirty_entries,
        "dirty_entries": dirty_entries,
        "tracked_files": len(tracked),
        "untracked_files": len(untracked),
        "ignored_files_not_hashed": ignored_count,
        "inventoried_tracked_and_untracked_files": len(records),
        "tracked_bytes": sum(
            record.size_bytes for record in records if record.state == "tracked"
        ),
        "category_counts": category_counts,
        "forbidden_tracked_paths": forbidden_tracked,
        "unknown_tracked_paths": unknown_tracked,
        "duplicate_python_definitions": duplicate_issues,
        "machine_local_paths_all": machine_paths,
        "machine_local_paths_blocking": blocking_machine_paths,
        "passed": not dirty_entries
        and not forbidden_tracked
        and not unknown_tracked
        and not duplicate_issues
        and not blocking_machine_paths,
    }
    return records, summary


def write_reports(
    output_dir: Path, records: list[FileRecord], summary: dict[str, object]
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "repository_inventory.json").write_text(
        json.dumps(
            {"summary": summary, "files": [asdict(record) for record in records]},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    with (output_dir / "repository_inventory.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(asdict(records[0]).keys()) if records else ["path"],
        )
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))
    (output_dir / "repository_audit_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check", action="store_true", help="return non-zero when policy fails"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help=(
            "report directory; defaults to "
            "$HOODIE_RUN_ROOT/audits/repository when configured"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()
    records, summary = inventory(root)

    output_dir = args.output_dir
    if output_dir is None:
        configured = os.environ.get("HOODIE_RUN_ROOT")
        if configured:
            output_dir = (
                Path(configured).expanduser().resolve() / "audits" / "repository"
            )
    if output_dir is not None:
        write_reports(output_dir, records, summary)

    concise = {
        "passed": summary["passed"],
        "head": summary["head"],
        "working_tree_clean": summary["working_tree_clean"],
        "tracked_files": summary["tracked_files"],
        "untracked_files": summary["untracked_files"],
        "forbidden_tracked_count": len(summary["forbidden_tracked_paths"]),
        "unknown_tracked_count": len(summary["unknown_tracked_paths"]),
        "duplicate_critical_definition_count": len(
            summary["duplicate_python_definitions"]
        ),
        "blocking_machine_local_path_count": len(
            summary["machine_local_paths_blocking"]
        ),
        "report_dir": str(output_dir) if output_dir is not None else None,
    }
    print(json.dumps(concise, sort_keys=True))
    return 1 if args.check and not bool(summary["passed"]) else 0


if __name__ == "__main__":
    sys.exit(main())
