from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path
import subprocess
from typing import Sequence


FEATURE_ID = "081-hoodie-proposed-method-fidelity-extraction"
FEATURE_NAME = "Feature 081 - HOODIE Proposed Method Fidelity Extraction"
READY_STATUS = "hoodie_proposed_fidelity_ready"
BLOCKED_STATUS = "hoodie_proposed_fidelity_blocked"
BASE_PAPER_TARGET = "HOODIE_PROPOSED"
SOURCE_PDF = "resources/papers/hoodie/original/HOODIE_paper.pdf"
SOURCE_OCR = "resources/papers/hoodie/ocr/merged.txt"

REQUIRED_COMPONENT_IDS: tuple[str, ...] = (
    "system_model",
    "architecture",
    "edge_agents",
    "state_space",
    "action_space",
    "reward_cost",
    "private_queue",
    "offloading_queue",
    "public_queue",
    "dqn_training",
    "double_dqn",
    "dueling_dqn",
    "lstm_forecast",
    "replay_memory",
    "inference",
    "pubsub_recovery",
    "baselines",
    "metrics",
    "simulation_parameters",
)

ALLOWED_PATH_PATTERNS: tuple[str, ...] = (
    "src/analysis/hoodie_proposed_fidelity/**",
    "tests/unit/test_hoodie_proposed_fidelity_*.py",
    "tests/integration/test_hoodie_proposed_fidelity_*.py",
)

FORBIDDEN_PATH_PATTERNS: tuple[str, ...] = (
    "specs/**",
    "src/environment/**",
    "src/training/**",
    "src/agents/**",
    "src/policies/**",
    "src/analysis/campaign_execution_engine/**",
    "src/analysis/result_aggregation_statistical_summary/**",
    "src/analysis/evaluation_ranking/**",
    "artifacts/**",
    "resources/**",
    "requirements*.txt",
    "pyproject.toml",
    "poetry.lock",
    "uv.lock",
    "Pipfile",
    "Pipfile.lock",
)

DEFAULT_CHANGED_FILES: tuple[str, ...] = (
    "src/analysis/hoodie_proposed_fidelity/__init__.py",
    "src/analysis/hoodie_proposed_fidelity/__main__.py",
    "src/analysis/hoodie_proposed_fidelity/config.py",
    "src/analysis/hoodie_proposed_fidelity/model.py",
    "src/analysis/hoodie_proposed_fidelity/paper_extract.py",
    "src/analysis/hoodie_proposed_fidelity/implementation_scan.py",
    "src/analysis/hoodie_proposed_fidelity/report.py",
    "src/analysis/hoodie_proposed_fidelity/runner.py",
    "tests/unit/test_hoodie_proposed_fidelity_model.py",
    "tests/unit/test_hoodie_proposed_fidelity_paper_extract.py",
    "tests/unit/test_hoodie_proposed_fidelity_implementation_scan.py",
    "tests/unit/test_hoodie_proposed_fidelity_report.py",
    "tests/unit/test_hoodie_proposed_fidelity_scope_guard.py",
    "tests/integration/test_hoodie_proposed_fidelity_report.py",
)

DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/hoodie_proposed_fidelity")


def _matches_any(path: str, patterns: Sequence[str]) -> bool:
    return any(fnmatch(path, pattern) for pattern in patterns)


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


def validate_scope(paths: Sequence[str] | None = None) -> list[str]:
    checked = list(DEFAULT_CHANGED_FILES if paths is None else paths)
    if paths is None:
        try:
            checked = _collect_git_paths()
        except Exception:
            checked = list(DEFAULT_CHANGED_FILES)
    for path in checked:
        if _matches_any(path, FORBIDDEN_PATH_PATTERNS):
            raise ValueError(f"forbidden path detected: {path}")
        if not _matches_any(path, ALLOWED_PATH_PATTERNS):
            raise ValueError(f"path is outside the Feature 081 scope: {path}")
    return checked
