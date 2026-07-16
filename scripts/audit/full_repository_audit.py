#!/usr/bin/env python3
"""Repository-wide inventory, classification, and cleanup planning.

This script is intentionally read-only with respect to project files. It writes
machine-readable audit outputs under artifacts/repository_audit/.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import subprocess
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts" / "repository_audit"
TEXT_SUFFIXES = {
    ".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".ini",
    ".cfg", ".csv", ".tsv", ".sh", ".js", ".mjs", ".cjs", ".html",
    ".css", ".xml", ".tex", ".rst", ".sql", ".gitignore",
}
CHECKPOINT_SUFFIXES = {".pt", ".pth", ".ckpt"}
GENERATED_SUFFIXES = CHECKPOINT_SUFFIXES | {".log", ".tmp", ".pyc", ".pyo", ".coverage"}


@dataclass(slots=True)
class FileRecord:
    path: str
    size_bytes: int
    sha256: str
    extension: str
    top_level: str
    category: str
    proposed_action: str
    rationale: str
    ignored_by_current_rules: bool
    empty: bool
    is_text: bool
    python_parse_ok: bool | None
    duplicate_group_size: int
    machine_local_path_hits: int
    checkpoint_like: bool


def git_bytes(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def git_text(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def tracked_paths() -> list[str]:
    return [
        raw.decode("utf-8", errors="surrogateescape")
        for raw in git_bytes("ls-files", "-z").split(b"\0")
        if raw
    ]


def ignored_tracked_paths() -> set[str]:
    proc = subprocess.run(
        ["git", "ls-files", "-ci", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
    )
    return {
        raw.decode("utf-8", errors="surrogateescape")
        for raw in proc.stdout.split(b"\0")
        if raw
    }


def classify(path: str, size: int) -> tuple[str, str, str]:
    p = Path(path)
    parts = p.parts
    top = parts[0] if parts else path
    suffix = p.suffix.lower()

    if path in {"README.md", "AGENTS.md", "pyproject.toml", "requirements.txt", ".gitignore"}:
        return "governance_or_packaging", "keep_and_revise", "Canonical repository entrypoint, policy, or packaging file."
    if top == "src":
        if len(parts) > 1 and parts[1] == "analysis":
            return "legacy_analysis_source", "review_then_archive_or_remove", "Large historical analysis surface overlaps the active scientific pipeline."
        return "core_source", "keep_and_consolidate", "Active simulator, policy, training, evaluation, or experiment source."
    if top in {"tests", "tests_supported", "tests_historical"}:
        if top == "tests_historical":
            return "historical_test", "archive_outside_active_suite", "Historical tests must not obscure the active acceptance gate."
        return "active_or_candidate_test", "consolidate_into_tests", "All active tests should use one canonical pytest tree."
    if top == "configs":
        return "configuration", "keep_and_normalize", "Experiment and runtime configuration."
    if top == "specs":
        return "historical_or_active_spec", "index_and_archive_superseded", "Specs require active/superseded classification."
    if top == "docs":
        if "run-logs" in parts:
            return "run_log", "retain_only_concise_current_logs", "Run logs are useful only when bounded and current."
        return "documentation", "keep_and_revise", "Project documentation."
    if top == "resources":
        return "scientific_reference", "keep_if_approved_and_deduplicated", "Paper and vendored reference material."
    if top == "artifacts":
        if any(token in parts for token in ("campaigns", "distributed", "releases", "smoke", "analysis")):
            return "generated_or_historical_artifact", "move_out_of_git_or_archive_index_only", "Generated runtime output should not live in the active Git tree."
        if any(token in parts for token in ("control", "reconciliation")):
            return "historical_control_artifact", "archive_index_only", "Control and reconciliation evidence should be centralized outside active runtime paths."
        return "artifact_unknown", "manual_review", "Artifact requires explicit scientific-reference versus generated-output decision."
    if top in {".claude", ".claude-flow", ".opencode", ".swarm"}:
        if path == "AGENTS.md":
            return "governance_or_packaging", "keep_and_revise", "Canonical agent instructions."
        return "agent_runtime_or_vendor_clutter", "remove_from_git", "Generic agent/runtime state does not belong in the scientific repository."
    if top == ".github":
        return "ci_workflow", "keep_only_required_workflows", "CI should contain only deterministic scientific and repository-quality gates."
    if top == "scripts":
        if len(parts) > 1 and parts[1] == "audit":
            return "audit_tool", "keep", "Repository audit and cleanup tooling."
        if len(parts) > 1 and parts[1] == "control":
            return "historical_control_script", "archive_or_remove", "Control materializers are separate from the active simulator workflow."
        return "script", "review_and_keep_if_referenced", "Operational script requires reference and ownership review."
    if suffix in CHECKPOINT_SUFFIXES or p.name == "checkpoint.pt":
        return "checkpoint_payload", "remove_from_git_and_externalize", "Checkpoint payloads must use bounded external run storage."
    if suffix in GENERATED_SUFFIXES:
        return "generated_runtime_file", "remove_from_git", "Generated runtime files are ignored and must not remain tracked."
    if p.name.endswith(".pid") or p.name == "daemon.pid":
        return "runtime_pid", "remove_from_git", "PID files are host-specific and unsafe when tracked."
    if p.name.startswith("temp_") or p.name.startswith("tmp_") or "trigger" in p.name.lower():
        return "temporary_transport", "remove_after_audit", "Temporary transport or trigger file."
    if size == 0:
        return "empty_placeholder", "remove_unless_required", "Empty placeholder files add noise and often duplicate installed tooling."
    return "uncategorized", "manual_review", "No safe automatic classification rule matched."


def text_content(path: Path, size: int) -> str | None:
    if size > 2_000_000:
        return None
    suffix = path.suffix.lower()
    if suffix not in TEXT_SUFFIXES and path.name not in {"README", "LICENSE", "Makefile", "Dockerfile", ".gitignore"}:
        return None
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def python_audit(path: Path, text: str | None) -> tuple[bool | None, dict[str, int], list[str]]:
    if path.suffix.lower() != ".py" or text is None:
        return None, {}, []
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError:
        return False, {}, []
    defs: Counter[str] = Counter()
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defs[node.name] += 1
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(("." * node.level) + (node.module or ""))
    return True, {name: count for name, count in defs.items() if count > 1}, imports


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    paths = tracked_paths()
    ignored = ignored_tracked_paths()
    raw: list[dict[str, object]] = []
    hash_to_paths: dict[str, list[str]] = defaultdict(list)
    duplicate_defs: dict[str, dict[str, int]] = {}
    imports_by_file: dict[str, list[str]] = {}
    parse_failures: list[str] = []
    machine_path_re = re.compile(r"/(?:Users|home)/[^/\s]+/")

    for rel in paths:
        path = ROOT / rel
        if not path.is_file():
            continue
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        hash_to_paths[digest].append(rel)
        text = text_content(path, len(data))
        parse_ok, dup_defs, imports = python_audit(path, text)
        if dup_defs:
            duplicate_defs[rel] = dup_defs
        if imports:
            imports_by_file[rel] = imports
        if parse_ok is False:
            parse_failures.append(rel)
        category, action, rationale = classify(rel, len(data))
        raw.append({
            "path": rel,
            "size_bytes": len(data),
            "sha256": digest,
            "extension": path.suffix.lower(),
            "top_level": Path(rel).parts[0],
            "category": category,
            "proposed_action": action,
            "rationale": rationale,
            "ignored_by_current_rules": rel in ignored,
            "empty": len(data) == 0,
            "is_text": text is not None,
            "python_parse_ok": parse_ok,
            "machine_local_path_hits": len(machine_path_re.findall(text or "")),
            "checkpoint_like": path.suffix.lower() in CHECKPOINT_SUFFIXES or path.name == "checkpoint.pt",
        })

    duplicates = {digest: entries for digest, entries in hash_to_paths.items() if len(entries) > 1}
    records = [
        FileRecord(**item, duplicate_group_size=len(hash_to_paths[str(item["sha256"])]))
        for item in raw
    ]

    category_counts = Counter(record.category for record in records)
    action_counts = Counter(record.proposed_action for record in records)
    top_stats: dict[str, dict[str, int]] = defaultdict(lambda: {"files": 0, "bytes": 0})
    for record in records:
        top_stats[record.top_level]["files"] += 1
        top_stats[record.top_level]["bytes"] += record.size_bytes

    inventory = {
        "schema_version": 1,
        "head_sha": git_text("rev-parse", "HEAD"),
        "tracked_file_count": len(records),
        "tracked_bytes": sum(record.size_bytes for record in records),
        "category_counts": dict(sorted(category_counts.items())),
        "action_counts": dict(sorted(action_counts.items())),
        "top_level": dict(sorted(top_stats.items())),
        "files": [asdict(record) for record in records],
    }
    findings = {
        "schema_version": 1,
        "head_sha": inventory["head_sha"],
        "tracked_ignored_files": sorted(ignored),
        "duplicate_content_groups": duplicates,
        "duplicate_definitions": duplicate_defs,
        "python_parse_failures": sorted(parse_failures),
        "machine_local_path_files": sorted(record.path for record in records if record.machine_local_path_hits),
        "checkpoint_payloads": sorted(record.path for record in records if record.checkpoint_like),
        "empty_files": sorted(record.path for record in records if record.empty),
        "large_files": [
            {"path": record.path, "size_bytes": record.size_bytes, "category": record.category}
            for record in sorted(records, key=lambda item: item.size_bytes, reverse=True)[:200]
        ],
        "imports_by_file": imports_by_file,
    }
    cleanup_plan = {
        "schema_version": 1,
        "head_sha": inventory["head_sha"],
        "main_goal": "Produce one installable, scientifically defensible HOODIE simulator with bounded external run storage and one verified path from paper contracts to Figures 8-11.",
        "phases": [
            {"phase": 1, "name": "Repository boundary", "actions": ["freeze production execution", "classify every tracked file", "remove tracked runtime state"]},
            {"phase": 2, "name": "Package and tests", "actions": ["consolidate package imports", "unify active pytest tree", "add clean-install gate"]},
            {"phase": 3, "name": "Storage safety", "actions": ["externalize runs", "bound checkpoints", "deduplicate and retain latest/best/final only"]},
            {"phase": 4, "name": "Scientific pipeline", "actions": ["one executor", "one verifier", "panel-specific metrics", "portable distributed bundles"]},
            {"phase": 5, "name": "Acceptance", "actions": ["fresh-checkout pilot", "repository hygiene gate", "freeze production package"]},
        ],
        "files_by_action": {
            action: sorted(record.path for record in records if record.proposed_action == action)
            for action in sorted(action_counts)
        },
    }

    (OUT / "repository_inventory.json").write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "repository_findings.json").write_text(json.dumps(findings, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "cleanup_plan.json").write_text(json.dumps(cleanup_plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = [
        "# Repository-wide audit summary",
        "",
        f"- Head: `{inventory['head_sha']}`",
        f"- Tracked files: **{inventory['tracked_file_count']}**",
        f"- Tracked bytes: **{inventory['tracked_bytes']}**",
        f"- Tracked files ignored by current rules: **{len(ignored)}**",
        f"- Duplicate-content groups: **{len(duplicates)}**",
        f"- Files with duplicate Python definitions: **{len(duplicate_defs)}**",
        f"- Python parse failures: **{len(parse_failures)}**",
        f"- Tracked checkpoint payloads: **{len(findings['checkpoint_payloads'])}**",
        "",
        "## Categories",
        "",
    ]
    summary.extend(f"- `{name}`: {count}" for name, count in sorted(category_counts.items()))
    summary.extend(["", "## Proposed actions", ""])
    summary.extend(f"- `{name}`: {count}" for name, count in sorted(action_counts.items()))
    summary.extend([
        "",
        "## Main goal",
        "",
        cleanup_plan["main_goal"],
        "",
        "Detailed per-file records are in `repository_inventory.json`.",
    ])
    (OUT / "AUDIT_SUMMARY.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(json.dumps({
        "head_sha": inventory["head_sha"],
        "tracked_file_count": inventory["tracked_file_count"],
        "tracked_bytes": inventory["tracked_bytes"],
        "tracked_ignored_files": len(ignored),
        "duplicate_content_groups": len(duplicates),
        "duplicate_definition_files": len(duplicate_defs),
        "checkpoint_payload_count": len(findings["checkpoint_payloads"]),
        "output_dir": str(OUT.relative_to(ROOT)),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
