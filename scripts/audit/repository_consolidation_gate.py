#!/usr/bin/env python3
"""Fail closed until the repository has one canonical HOODIE execution surface.

This gate is intentionally stricter than the general file inventory.  The
inventory classifies every file; this module decides whether the active tree is
small and consolidated enough to permit scientific execution.
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import subprocess
import sys
import tomllib
from typing import Iterable


ALLOWED_TRACKED_ARTIFACT_PREFIXES = ("artifacts/approved/",)
LEGACY_ACTIVE_PREFIXES = (
    "hoodie/",
    "tests_supported/",
    "tests_historical/",
)
TRANSITIONAL_EXACT = {
    "src/hoodie/experiments/cli_v2.py",
    "src/hoodie/experiments/distributed_v2.py",
    "src/hoodie/experiments/production_campaign.py",
}
CANONICAL_REQUIRED = {
    "src/hoodie/experiments/campaign.py",
    "src/hoodie/experiments/executor.py",
    "src/hoodie/experiments/distributed.py",
    "src/hoodie/experiments/verification.py",
    "src/hoodie/storage/checkpoints.py",
    "src/hoodie/visualization/figures_8_11.py",
    "tests/unit",
    "tests/integration",
    "tests/acceptance",
}
ACTIVE_PYTHON_PREFIXES = ("src/hoodie/",)
ACTIVE_PYTHON_EXCLUDE = ()


@dataclass(frozen=True, slots=True)
class GateResult:
    tracked_artifact_paths: tuple[str, ...]
    legacy_active_paths: tuple[str, ...]
    transitional_modules: tuple[str, ...]
    legacy_src_imports: tuple[str, ...]
    active_echo_dependencies: tuple[str, ...]
    packaging_issues: tuple[str, ...]
    missing_canonical_paths: tuple[str, ...]
    passed: bool


def _git(root: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def repository_root() -> Path:
    output = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout
    return Path(output.strip()).resolve()


def tracked_paths(root: Path) -> tuple[str, ...]:
    payload = _git(root, "ls-files", "-z")
    return tuple(
        sorted(
            part.decode("utf-8", errors="surrogateescape")
            for part in payload.split(b"\0")
            if part
        )
    )


def _artifact_issues(paths: Iterable[str]) -> tuple[str, ...]:
    return tuple(
        path
        for path in paths
        if path.startswith("artifacts/")
        and not path.startswith(ALLOWED_TRACKED_ARTIFACT_PREFIXES)
    )


def _legacy_active_issues(paths: Iterable[str]) -> tuple[str, ...]:
    return tuple(path for path in paths if path.startswith(LEGACY_ACTIVE_PREFIXES))


def _transitional_issues(paths: Iterable[str]) -> tuple[str, ...]:
    issues: list[str] = []
    for path in paths:
        if path in TRANSITIONAL_EXACT:
            issues.append(path)
            continue
        if path.startswith("src/hoodie/experiments/") and (
            path.endswith("_patch.py") or path.endswith("_v2.py")
        ):
            issues.append(path)
    return tuple(sorted(set(issues)))


def _import_issues(root: Path, paths: Iterable[str]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    legacy: list[str] = []
    echo: list[str] = []
    for relative in paths:
        if not relative.endswith(".py") or not relative.startswith(ACTIVE_PYTHON_PREFIXES):
            continue
        source = root / relative
        try:
            tree = ast.parse(source.read_text(encoding="utf-8"), filename=relative)
        except (OSError, UnicodeDecodeError, SyntaxError) as exc:
            legacy.append(f"{relative}:parse_error:{exc}")
            continue
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.append(node.module)
            for module in modules:
                if module == "src" or module.startswith("src."):
                    legacy.append(f"{relative}:{module}")
                if module.startswith("src.echo") or module.startswith("hoodie.echo"):
                    echo.append(f"{relative}:{module}")
    return tuple(sorted(set(legacy))), tuple(sorted(set(echo)))


def _packaging_issues(root: Path) -> tuple[str, ...]:
    path = root / "pyproject.toml"
    if not path.is_file():
        return ("pyproject.toml:missing",)
    payload = tomllib.loads(path.read_text(encoding="utf-8"))
    issues: list[str] = []

    scripts = payload.get("project", {}).get("scripts", {})
    if scripts.get("hoodie-experiments") != "hoodie.experiments.cli:main":
        issues.append("project.scripts.hoodie-experiments must be hoodie.experiments.cli:main")

    setuptools = payload.get("tool", {}).get("setuptools", {})
    package_dir = setuptools.get("package-dir", {})
    if package_dir != {"": "src"}:
        issues.append("tool.setuptools.package-dir must be {'': 'src'}")

    finder = setuptools.get("packages", {}).get("find", {})
    if finder.get("where") != ["src"]:
        issues.append("tool.setuptools.packages.find.where must be ['src']")
    if finder.get("include") != ["hoodie*"]:
        issues.append("tool.setuptools.packages.find.include must be ['hoodie*']")

    pytest = payload.get("tool", {}).get("pytest", {}).get("ini_options", {})
    testpaths = pytest.get("testpaths", [])
    expected = ["tests/unit", "tests/integration", "tests/acceptance"]
    if testpaths != expected:
        issues.append(f"pytest testpaths must be exactly {expected!r}")
    return tuple(issues)


def _missing_canonical(root: Path) -> tuple[str, ...]:
    return tuple(sorted(path for path in CANONICAL_REQUIRED if not (root / path).exists()))


def evaluate(root: Path) -> GateResult:
    paths = tracked_paths(root)
    legacy_imports, echo_dependencies = _import_issues(root, paths)
    artifact_paths = _artifact_issues(paths)
    legacy_paths = _legacy_active_issues(paths)
    transitional = _transitional_issues(paths)
    packaging = _packaging_issues(root)
    missing = _missing_canonical(root)
    passed = not any(
        (
            artifact_paths,
            legacy_paths,
            transitional,
            legacy_imports,
            echo_dependencies,
            packaging,
            missing,
        )
    )
    return GateResult(
        tracked_artifact_paths=artifact_paths,
        legacy_active_paths=legacy_paths,
        transitional_modules=transitional,
        legacy_src_imports=legacy_imports,
        active_echo_dependencies=echo_dependencies,
        packaging_issues=packaging,
        missing_canonical_paths=missing,
        passed=passed,
    )


def _write_report(path: Path, result: GateResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--report", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repository_root()
    result = evaluate(root)
    report = args.report
    if report is None and os.environ.get("HOODIE_RUN_ROOT"):
        report = Path(os.environ["HOODIE_RUN_ROOT"]).expanduser().resolve() / "audits" / "repository" / "consolidation_gate.json"
    if report is not None:
        _write_report(report, result)
    concise = {
        "passed": result.passed,
        "tracked_artifact_count": len(result.tracked_artifact_paths),
        "legacy_active_path_count": len(result.legacy_active_paths),
        "transitional_module_count": len(result.transitional_modules),
        "legacy_src_import_count": len(result.legacy_src_imports),
        "active_echo_dependency_count": len(result.active_echo_dependencies),
        "packaging_issue_count": len(result.packaging_issues),
        "missing_canonical_path_count": len(result.missing_canonical_paths),
        "report": str(report) if report is not None else None,
    }
    print(json.dumps(concise, sort_keys=True))
    return 1 if args.check and not result.passed else 0


if __name__ == "__main__":
    sys.exit(main())
