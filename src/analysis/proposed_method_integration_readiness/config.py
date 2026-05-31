from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Sequence


FEATURE_ID = "075-proposed-method-integration-readiness"
FEATURE_NAME = "Feature 075 - Proposed Method Integration Readiness"
IMPLEMENTATION_BRANCH = "075-proposed-integration-readiness"
BASE_FEATURE_074_COMMIT = "b9d847d5f0777e17d223b7f78ff738bff79e8b0e"

FEATURE_075_SPEC = Path("specs/075-proposed-method-integration-readiness/spec.md")
FEATURE_075_PLAN = Path("specs/075-proposed-method-integration-readiness/plan.md")
FEATURE_075_RESEARCH = Path("specs/075-proposed-method-integration-readiness/research.md")
FEATURE_075_DATA_MODEL = Path("specs/075-proposed-method-integration-readiness/data-model.md")
FEATURE_075_TASKS = Path("specs/075-proposed-method-integration-readiness/tasks.md")
FEATURE_075_QUICKSTART = Path("specs/075-proposed-method-integration-readiness/quickstart.md")
FEATURE_075_CHECKLIST = Path("specs/075-proposed-method-integration-readiness/checklists/requirements.md")
FEATURE_075_CONTRACT = Path("specs/075-proposed-method-integration-readiness/contracts/proposed-method-integration-report-schema.md")

DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/proposed_method_integration_readiness")

VALIDATION_COMMANDS = (
    "src/.venvmac/bin/python -m unittest tests.unit.test_policy_registry tests.unit.test_baseline_policy_fidelity tests.unit.test_mleo_policy tests.integration.test_baseline_policy_fidelity_flow",
    "src/.venvmac/bin/python -m unittest tests.unit.test_full_hoodie_mechanism_fidelity_batch_report tests.unit.test_full_hoodie_mechanism_fidelity_batch_scope_guard tests.integration.test_full_hoodie_mechanism_fidelity_batch_report",
    "src/.venvmac/bin/python -m unittest tests.unit.test_topology_timeout_reward_fidelity_report tests.unit.test_topology_timeout_reward_fidelity_models tests.unit.test_topology_timeout_reward_fidelity_scope_guard tests.integration.test_topology_timeout_reward_fidelity_report",
    "src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_runtime_paper_faithful_semantics_alignment_*.py'",
    "src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_runtime_paper_faithful_semantics_alignment_*.py'",
    "src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_end_to_end_hoodie_golden_trace_validation_*.py'",
    "src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_end_to_end_hoodie_golden_trace_validation_*.py'",
    "src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_controlled_evaluation_batch_readiness_*.py'",
    "src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_controlled_evaluation_batch_readiness_*.py'",
    "src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_baseline_policy_comparative_evaluation_readiness_*.py'",
    "src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_baseline_policy_comparative_evaluation_readiness_*.py'",
    "src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_proposed_method_integration_readiness_*.py'",
    "src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_proposed_method_integration_readiness_*.py'",
    "git diff --check",
)

ALLOWED_PATH_PREFIXES = (
    "specs/075-proposed-method-integration-readiness/",
    "src/analysis/proposed_method_integration_readiness/",
    "tests/unit/test_proposed_method_integration_readiness_",
    "tests/integration/test_proposed_method_integration_readiness_",
)

FORBIDDEN_PATH_PREFIXES = (
    "src/training/",
    "src/agents/",
    "src/policies/",
    "src/environment/",
    "artifacts/",
    "resources/",
    "specs/076-",
    "src/analysis/end_to_end_hoodie_golden_trace_validation/",
    "src/analysis/runtime_paper_faithful_semantics_alignment/",
    "src/analysis/controlled_evaluation_batch_readiness/",
    "src/analysis/topology_timeout_reward_fidelity/",
    "src/analysis/baseline_policy_comparative_evaluation_readiness/",
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

DEFAULT_CHANGED_FILES = (
    "specs/075-proposed-method-integration-readiness/plan.md",
    "specs/075-proposed-method-integration-readiness/data-model.md",
    "specs/075-proposed-method-integration-readiness/contracts/proposed-method-integration-report-schema.md",
    "specs/075-proposed-method-integration-readiness/tasks.md",
    "src/analysis/proposed_method_integration_readiness/__init__.py",
    "src/analysis/proposed_method_integration_readiness/__main__.py",
    "src/analysis/proposed_method_integration_readiness/config.py",
    "src/analysis/proposed_method_integration_readiness/model.py",
    "src/analysis/proposed_method_integration_readiness/report.py",
    "src/analysis/proposed_method_integration_readiness/runner.py",
    "tests/unit/test_proposed_method_integration_readiness_model.py",
    "tests/unit/test_proposed_method_integration_readiness_scoring.py",
    "tests/unit/test_proposed_method_integration_readiness_report.py",
    "tests/unit/test_proposed_method_integration_readiness_scope_guard.py",
    "tests/integration/test_proposed_method_integration_readiness_report.py",
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
    output = _git_output("diff", "--name-only", f"{BASE_FEATURE_074_COMMIT}...HEAD")
    return [line for line in output.splitlines() if line]


def _all_paths() -> list[str]:
    return [*_tracked_paths(), *_staged_paths(), *_diff_paths()]


def _is_allowed(path: str) -> bool:
    if not path:
        return True
    if Path(path).name in DEPENDENCY_FILE_NAMES:
        return False
    if path.startswith("src/analysis/") and not path.startswith("src/analysis/proposed_method_integration_readiness/"):
        return False
    if any(path.startswith(prefix) for prefix in FORBIDDEN_PATH_PREFIXES):
        return False
    return any(path.startswith(prefix) for prefix in ALLOWED_PATH_PREFIXES)


def validate_scope(paths: Sequence[str] | None = None) -> list[str]:
    checked = list(paths) if paths is not None else _all_paths()
    forbidden = [path for path in checked if path and not _is_allowed(path)]
    if forbidden:
        raise RuntimeError("Dirty or diff paths outside approved Feature 075 scope: " + ", ".join(sorted(set(forbidden))))
    return checked
