from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path
import subprocess
from collections.abc import Sequence


FEATURE_ID = "079-result-aggregation-statistical-summary"
FEATURE_NAME = "Feature 079 - Result Aggregation Statistical Summary"
READY_STATUS = "result_aggregation_statistical_summary_ready"
BLOCKED_STATUS = "result_aggregation_statistical_summary_with_blockers"
DEPENDENCY_FEATURES: tuple[str, ...] = (
    "078-campaign-execution-engine",
    "077-experimental-campaign-readiness",
)
INPUT_FEATURE_ID = "078-campaign-execution-engine"
INPUT_READY_STATUS = "campaign_execution_engine_ready"
WORKLOAD_LEVELS: tuple[str, ...] = ("low", "medium", "high")
DEADLINE_PRESSURE_LEVELS: tuple[str, ...] = ("relaxed", "moderate", "tight")
REQUIRED_POLICY_IDS: tuple[str, ...] = ("FLC", "VO", "HO", "RO", "BCO", "MLEO", "PROPOSED_DCQ")
REQUIRED_SCENARIO_IDS: tuple[str, ...] = (
    "light_load_no_deadline_pressure",
    "tight_deadline_pressure",
    "legal_horizontal_offload",
    "illegal_horizontal_destination_attempt",
    "cloud_vertical_fallback",
    "timeout_drop_case",
    "mixed_local_horizontal_cloud_candidates",
)
REQUIRED_METRIC_NAMES: tuple[str, ...] = (
    "completion_rate",
    "timeout_drop_rate",
    "unavailable_drop_rate",
    "deadline_violation_rate",
    "average_delay",
    "average_reward",
    "total_reward",
)
SUMMARY_FIELD_NAMES: tuple[str, ...] = ("mean", "std", "min", "max", "count", "ci95_low", "ci95_high")
GROUPING_TYPES: tuple[str, ...] = (
    "policy",
    "policy_scenario",
    "policy_workload",
    "policy_deadline",
    "policy_workload_deadline",
)
EXPECTED_GROUPING_COUNTS: dict[str, int] = {
    "policy": 7,
    "policy_scenario": 7,
    "policy_workload": 3,
    "policy_deadline": 3,
    "policy_workload_deadline": 9,
}
POLICY_FAMILY_BY_ID: dict[str, str] = {
    "FLC": "full_local_computing",
    "VO": "vertical_offloading",
    "HO": "horizontal_offloading",
    "RO": "random_offloading",
    "BCO": "balanced_cooperation_offloading",
    "MLEO": "minimum_latency_estimate_offloading",
    "PROPOSED_DCQ": "proposed_deadline_queueing",
}
ALLOWED_PATH_PATTERNS: tuple[str, ...] = (
    "src/analysis/result_aggregation_statistical_summary/**",
    "tests/unit/test_result_aggregation_statistical_summary_*.py",
    "tests/integration/test_result_aggregation_statistical_summary_*.py",
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
    "src/analysis/*080*",
    "tests/unit/test_*080*",
    "tests/integration/test_*080*",
)
DEFAULT_CHANGED_FILES: tuple[str, ...] = (
    "src/analysis/result_aggregation_statistical_summary/__init__.py",
    "src/analysis/result_aggregation_statistical_summary/__main__.py",
    "src/analysis/result_aggregation_statistical_summary/config.py",
    "src/analysis/result_aggregation_statistical_summary/model.py",
    "src/analysis/result_aggregation_statistical_summary/aggregator.py",
    "src/analysis/result_aggregation_statistical_summary/report.py",
    "tests/unit/test_result_aggregation_statistical_summary_model.py",
    "tests/unit/test_result_aggregation_statistical_summary_report.py",
    "tests/unit/test_result_aggregation_statistical_summary_scope_guard.py",
    "tests/integration/test_result_aggregation_statistical_summary_report.py",
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
            raise ValueError(f"path is outside the Feature 079 scope: {path}")
    return checked_paths
