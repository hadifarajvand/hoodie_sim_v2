from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Sequence

FEATURE_ID = "072-end-to-end-hoodie-golden-trace-validation"
FEATURE_NAME = "Feature 072 - End-to-End HOODIE Golden Trace Validation"
IMPLEMENTATION_BRANCH = "072-golden-trace-validation"
BASE_FEATURE_071_COMMIT = "4a3b33388074e60aa4462ce4fb71e282cfccc81c"

FEATURE_072_SPEC = Path("specs/072-end-to-end-hoodie-golden-trace-validation/spec.md")
FEATURE_072_PLAN = Path("specs/072-end-to-end-hoodie-golden-trace-validation/plan.md")
FEATURE_072_RESEARCH = Path("specs/072-end-to-end-hoodie-golden-trace-validation/research.md")
FEATURE_072_DATA_MODEL = Path("specs/072-end-to-end-hoodie-golden-trace-validation/data-model.md")
FEATURE_072_TASKS = Path("specs/072-end-to-end-hoodie-golden-trace-validation/tasks.md")
FEATURE_072_QUICKSTART = Path("specs/072-end-to-end-hoodie-golden-trace-validation/quickstart.md")
FEATURE_072_CHECKLIST = Path("specs/072-end-to-end-hoodie-golden-trace-validation/checklists/requirements.md")
FEATURE_072_CONTRACT = Path("specs/072-end-to-end-hoodie-golden-trace-validation/contracts/golden-trace-report-schema.md")

ALLOWED_PATH_PREFIXES = (
    "specs/072-end-to-end-hoodie-golden-trace-validation/",
    "src/analysis/end_to_end_hoodie_golden_trace_validation/",
    "tests/unit/test_end_to_end_hoodie_golden_trace_validation_",
    "tests/integration/test_end_to_end_hoodie_golden_trace_validation_",
)

FORBIDDEN_PATH_PREFIXES = (
    "src/training/",
    "src/agents/",
    "artifacts/",
    "resources/",
    "specs/073-",
)

DEPENDENCY_FILE_NAMES = {
    "requirements.txt",
    "requirements-dev.txt",
    "pyproject.toml",
    "poetry.lock",
    "uv.lock",
    "Pipfile",
    "Pipfile.lock",
}

VALIDATION_COMMANDS = (
    "src/.venvmac/bin/python -m unittest tests.unit.test_policy_registry tests.unit.test_baseline_policy_fidelity tests.unit.test_mleo_policy tests.integration.test_baseline_policy_fidelity_flow",
    "src/.venvmac/bin/python -m unittest tests.unit.test_full_hoodie_mechanism_fidelity_batch_report tests.unit.test_full_hoodie_mechanism_fidelity_batch_scope_guard tests.integration.test_full_hoodie_mechanism_fidelity_batch_report",
    "src/.venvmac/bin/python -m unittest tests.unit.test_topology_timeout_reward_fidelity_report tests.unit.test_topology_timeout_reward_fidelity_models tests.unit.test_topology_timeout_reward_fidelity_scope_guard tests.integration.test_topology_timeout_reward_fidelity_report",
    "src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_runtime_paper_faithful_semantics_alignment_*.py'",
    "src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_runtime_paper_faithful_semantics_alignment_*.py'",
    "src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_end_to_end_hoodie_golden_trace_validation_*.py'",
    "src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_end_to_end_hoodie_golden_trace_validation_*.py'",
    "git diff --check",
)

DEFAULT_CHANGED_FILES = (
    "specs/072-end-to-end-hoodie-golden-trace-validation/tasks.md",
    "src/analysis/end_to_end_hoodie_golden_trace_validation/__init__.py",
    "src/analysis/end_to_end_hoodie_golden_trace_validation/__main__.py",
    "src/analysis/end_to_end_hoodie_golden_trace_validation/config.py",
    "src/analysis/end_to_end_hoodie_golden_trace_validation/model.py",
    "src/analysis/end_to_end_hoodie_golden_trace_validation/report.py",
    "src/analysis/end_to_end_hoodie_golden_trace_validation/runner.py",
    "tests/unit/test_end_to_end_hoodie_golden_trace_validation_model.py",
    "tests/unit/test_end_to_end_hoodie_golden_trace_validation_scenarios.py",
    "tests/unit/test_end_to_end_hoodie_golden_trace_validation_report.py",
    "tests/unit/test_end_to_end_hoodie_golden_trace_validation_scope_guard.py",
    "tests/integration/test_end_to_end_hoodie_golden_trace_validation_report.py",
)


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
    output = _git_output("diff", "--name-only", f"{BASE_FEATURE_071_COMMIT}...HEAD")
    return [line for line in output.splitlines() if line]


def _all_paths() -> list[str]:
    return [*_tracked_paths(), *_staged_paths(), *_diff_paths()]


def _is_allowed(path: str) -> bool:
    if Path(path).name in DEPENDENCY_FILE_NAMES:
        return False
    if any(path.startswith(prefix) for prefix in FORBIDDEN_PATH_PREFIXES):
        return False
    if path.startswith("src/analysis/") and "073" in path:
        return False
    return any(path.startswith(prefix) for prefix in ALLOWED_PATH_PREFIXES)


def validate_scope(paths: Sequence[str] | None = None) -> list[str]:
    checked = list(paths) if paths is not None else _all_paths()
    forbidden = [path for path in checked if path and not _is_allowed(path)]
    if forbidden:
        raise RuntimeError("Dirty or diff paths outside approved Feature 072 scope: " + ", ".join(sorted(set(forbidden))))
    return checked
