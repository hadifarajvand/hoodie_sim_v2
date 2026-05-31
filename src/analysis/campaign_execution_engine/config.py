from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path
import subprocess
from typing import Sequence

from src.analysis.proposed_method_integration_readiness.model import PROPOSED_METHOD_POLICY_ID


FEATURE_ID = "078-campaign-execution-engine"
FEATURE_NAME = "Feature 078 - Campaign Execution Engine"
READY_STATUS = "campaign_execution_engine_ready"
BLOCKED_STATUS = "campaign_execution_engine_with_blockers"
DEPENDENCY_FEATURES: tuple[str, ...] = (
    "076-combined-baseline-proposed-comparative-readiness",
    "077-experimental-campaign-readiness",
)
REQUIRED_POLICY_IDS: tuple[str, ...] = ("FLC", "VO", "HO", "RO", "BCO", "MLEO", PROPOSED_METHOD_POLICY_ID)
REQUIRED_SCENARIO_IDS: tuple[str, ...] = (
    "light_load_no_deadline_pressure",
    "tight_deadline_pressure",
    "legal_horizontal_offload",
    "illegal_horizontal_destination_attempt",
    "cloud_vertical_fallback",
    "timeout_drop_case",
    "mixed_local_horizontal_cloud_candidates",
)
SEED_IDS: tuple[str, ...] = ("seed-001", "seed-002", "seed-003")
SEED_VALUES: tuple[int, ...] = (11, 17, 23)
SEED_SOURCE = "deterministic_campaign_schedule_v1"
WORKLOAD_LEVELS: tuple[str, ...] = ("low", "medium", "high")
DEADLINE_PRESSURE_LEVELS: tuple[str, ...] = ("relaxed", "moderate", "tight")
TOPOLOGY_MODE = "paper_figure_7"
RUNTIME_MODE = "paper"
EXPECTED_GRID_SIZE_FORMULA = "policy_count * scenario_count * seed_count * workload_count * deadline_pressure_count"
EXPECTED_ROW_COUNT_PER_SEED = len(REQUIRED_POLICY_IDS) * len(REQUIRED_SCENARIO_IDS) * len(WORKLOAD_LEVELS) * len(DEADLINE_PRESSURE_LEVELS)
ALLOWED_PATH_PATTERNS: tuple[str, ...] = (
    "src/analysis/campaign_execution_engine/**",
    "tests/unit/test_campaign_execution_engine_*.py",
    "tests/integration/test_campaign_execution_engine_*.py",
)
FORBIDDEN_PATH_PATTERNS: tuple[str, ...] = (
    "specs/**",
    "src/environment/**",
    "src/policies/**",
    "src/training/**",
    "src/agents/**",
    "artifacts/**",
    "resources/**",
    "requirements*.txt",
    "pyproject.toml",
    "poetry.lock",
    "uv.lock",
    "Pipfile",
    "Pipfile.lock",
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "src/analysis/*079*",
    "tests/unit/test_*079*",
    "tests/integration/test_*079*",
)
DEFAULT_CHANGED_FILES: tuple[str, ...] = (
    "src/analysis/campaign_execution_engine/__init__.py",
    "src/analysis/campaign_execution_engine/__main__.py",
    "src/analysis/campaign_execution_engine/config.py",
    "src/analysis/campaign_execution_engine/model.py",
    "src/analysis/campaign_execution_engine/report.py",
    "src/analysis/campaign_execution_engine/runner.py",
    "tests/unit/test_campaign_execution_engine_model.py",
    "tests/unit/test_campaign_execution_engine_report.py",
    "tests/unit/test_campaign_execution_engine_scope_guard.py",
    "tests/integration/test_campaign_execution_engine_report.py",
)


def _collect_git_paths() -> list[str]:
    result = subprocess.run(
        ["git", "status", "--short", "--untracked-files=all"],
        check=True,
        capture_output=True,
        text=True,
    )
    paths: list[str] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        path = line[3:].strip()
        if path:
            paths.append(path)
    return paths


def _matches_any(path: str, patterns: Sequence[str]) -> bool:
    return any(fnmatch(path, pattern) for pattern in patterns)


def validate_scope(paths: Sequence[str] | None = None) -> list[str]:
    checked_paths = list(DEFAULT_CHANGED_FILES if paths is None else paths)
    if paths is None:
        try:
            checked_paths = _collect_git_paths()
        except Exception:
            checked_paths = list(DEFAULT_CHANGED_FILES)
    for path in checked_paths:
        if _matches_any(path, FORBIDDEN_PATH_PATTERNS):
            raise ValueError(f"forbidden path detected: {path}")
        if not _matches_any(path, ALLOWED_PATH_PATTERNS):
            raise ValueError(f"path is outside the Feature 078 scope: {path}")
    return checked_paths
