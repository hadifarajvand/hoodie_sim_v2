from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path
import subprocess
from typing import Sequence


FEATURE_ID = "080-hoodie-proposed-method"
FEATURE_NAME = "Feature 080 - HOODIE Proposed Method Implementation"
READY_STATUS = "hoodie_proposed_method_ready"
BLOCKED_STATUS = "hoodie_proposed_method_blocked"
TARGET_METHOD_ID = "HOODIE_PROPOSED"

REQUIRED_COMPONENT_IDS: tuple[str, ...] = (
    "hybrid_action_model",
    "private_queue_timing",
    "offloading_queue_timing",
    "public_queue_timing",
    "reward_cost_model",
    "distributed_edge_agent_decision_model",
    "dqn_interface",
    "double_dqn_target_rule",
    "dueling_dqn_value_advantage_interface",
    "lstm_forecast_recovery_interface",
    "replay_memory_interface",
    "epsilon_greedy_training_schedule",
    "inference_mode_epsilon_zero",
    "pubsub_recovery_metadata",
)

ALLOWED_COMPONENT_STATUSES: tuple[str, ...] = ("implemented", "partial", "missing")
ALLOWED_READINESS_LEVELS: tuple[str, ...] = ("blocked", "partial", "mostly_implemented", "fully_implemented")

ALLOWED_PATH_PATTERNS: tuple[str, ...] = (
    "specs/080-evaluation-ranking/**",
    "src/analysis/hoodie_proposed_method/**",
    "tests/unit/test_hoodie_proposed_method_*.py",
    "tests/integration/test_hoodie_proposed_method_*.py",
)

FORBIDDEN_PATH_PATTERNS: tuple[str, ...] = (
    "src/analysis/evaluation_ranking/**",
    "src/analysis/hoodie_proposed_fidelity/**",
    "src/analysis/baseline_policy_comparative_evaluation_readiness/**",
    "src/analysis/combined_baseline_proposed_comparative_readiness/**",
    "src/analysis/proposed_method_integration_readiness/**",
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
)

DEFAULT_CHANGED_FILES: tuple[str, ...] = (
    "specs/080-evaluation-ranking/plan.md",
    "specs/080-evaluation-ranking/checklists/requirements.md",
    "specs/080-evaluation-ranking/checklists/scope.md",
    "src/analysis/hoodie_proposed_method/__init__.py",
    "src/analysis/hoodie_proposed_method/__main__.py",
    "src/analysis/hoodie_proposed_method/action_model.py",
    "src/analysis/hoodie_proposed_method/communication_model.py",
    "src/analysis/hoodie_proposed_method/config.py",
    "src/analysis/hoodie_proposed_method/formulas.py",
    "src/analysis/hoodie_proposed_method/learning_model.py",
    "src/analysis/hoodie_proposed_method/model.py",
    "src/analysis/hoodie_proposed_method/queue_model.py",
    "src/analysis/hoodie_proposed_method/reward_model.py",
    "src/analysis/hoodie_proposed_method/report.py",
    "src/analysis/hoodie_proposed_method/runner.py",
    "tests/unit/test_hoodie_proposed_method_model.py",
    "tests/unit/test_hoodie_proposed_method_components.py",
    "tests/unit/test_hoodie_proposed_method_learning.py",
    "tests/unit/test_hoodie_proposed_method_scope_guard.py",
    "tests/integration/test_hoodie_proposed_method_report.py",
)

DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/hoodie_proposed_method")


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
            raise ValueError(f"path is outside the Feature 080 scope: {path}")
    return checked
