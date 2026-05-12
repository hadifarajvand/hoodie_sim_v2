from __future__ import annotations

from pathlib import Path

from .registry import write_user_approved_assumption_registry
from .report import write_assumption_patch_report, build_assumption_patch_report


def run_user_approved_assumption_patch_registry(repo_root: Path | None = None) -> tuple[Path, Path, Path]:
    root = repo_root or Path.cwd()
    registry_path = write_user_approved_assumption_registry(root)
    report = build_assumption_patch_report(root)
    report_json, report_md = write_assumption_patch_report(report, root / "artifacts/analysis/user-approved-assumption-patch-registry")
    return registry_path, report_json, report_md

