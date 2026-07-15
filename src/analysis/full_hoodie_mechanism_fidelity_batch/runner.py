from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
import json
import subprocess
from typing import Any

from .config import ALLOWED_PATH_PREFIXES, DEPENDENCY_FILE_NAMES, FEATURE_ID, FORBIDDEN_PATH_PREFIXES
from .report import build_feature_069_report, render_feature_069_report, write_feature_069_report


def _git_output(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def _tracked_paths() -> list[str]:
    result = subprocess.run(["git", "status", "--short"], check=True, capture_output=True, text=True)
    paths: list[str] = []
    for line in result.stdout.splitlines():
        if len(line) >= 4:
            path = line[3:].strip()
            if path:
                paths.append(path)
    return paths


def _staged_paths() -> list[str]:
    output = _git_output("diff", "--cached", "--name-only")
    return [line for line in output.splitlines() if line]


def _diff_paths() -> list[str]:
    output = _git_output("diff", "--name-only", "origin/origin/main...HEAD")
    return [line for line in output.splitlines() if line]


def _all_paths() -> list[str]:
    return [*_tracked_paths(), *_staged_paths(), *_diff_paths()]


def _is_allowed(path: str) -> bool:
    if Path(path).name in DEPENDENCY_FILE_NAMES:
        return False
    if any(path.startswith(prefix) for prefix in FORBIDDEN_PATH_PREFIXES):
        return False
    return any(path.startswith(prefix) for prefix in ALLOWED_PATH_PREFIXES)


def validate_scope(paths: Sequence[str] | None = None) -> list[str]:
    checked = list(paths) if paths is not None else _all_paths()
    forbidden = [path for path in checked if path and not _is_allowed(path)]
    if forbidden:
        raise RuntimeError("Dirty or diff paths outside approved Feature 069 scope: " + ", ".join(sorted(set(forbidden))))
    return checked


def build_report() -> Any:
    changed_files = _diff_paths()
    validate_scope()
    return build_feature_069_report(changed_files=changed_files)


def run(output_dir: Path | str | None = None) -> Any:
    report = build_report()
    if output_dir is not None:
        return report, write_feature_069_report(report, output_dir)
    return report


def main(argv: Sequence[str] | None = None) -> int:
    report = build_report()
    if argv and "--json" in argv:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(render_feature_069_report(report))
    return 0
