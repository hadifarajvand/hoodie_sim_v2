from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Sequence

FEATURE_ID = "071-runtime-paper-faithful-semantics-alignment"
FEATURE_NAME = "Feature 071 - Runtime Paper-Faithful Semantics Alignment"
IMPLEMENTATION_BRANCH = "071-runtime-paper-faithful-semantics-alignment"
BASE_FEATURE_070_COMMIT = "3851cd3be63de09189d4ed45c038b34c9ca57aee"

FEATURE_071_SPEC = Path("specs/071-runtime-paper-faithful-semantics-alignment/spec.md")
FEATURE_071_PLAN = Path("specs/071-runtime-paper-faithful-semantics-alignment/plan.md")
FEATURE_071_RESEARCH = Path("specs/071-runtime-paper-faithful-semantics-alignment/research.md")
FEATURE_071_DATA_MODEL = Path("specs/071-runtime-paper-faithful-semantics-alignment/data-model.md")
FEATURE_071_TASKS = Path("specs/071-runtime-paper-faithful-semantics-alignment/tasks.md")
FEATURE_071_QUICKSTART = Path("specs/071-runtime-paper-faithful-semantics-alignment/quickstart.md")
FEATURE_071_CHECKLIST = Path("specs/071-runtime-paper-faithful-semantics-alignment/checklists/requirements.md")
FEATURE_071_CONTRACT = Path("specs/071-runtime-paper-faithful-semantics-alignment/contracts/runtime-paper-faithful-semantics-report-schema.md")
FEATURE_071_IMPLEMENTATION_PROMPT = Path("specs/071-runtime-paper-faithful-semantics-alignment/implementation-prompt.md")

ALLOWED_PATH_PREFIXES = (
    "specs/071-runtime-paper-faithful-semantics-alignment/",
    "src/analysis/runtime_paper_faithful_semantics_alignment/",
    "src/environment/paper_timeout.py",
    "src/environment/deadline_rules.py",
    "src/environment/reward_timing.py",
    "src/environment/runtime_model.py",
    "tests/unit/test_runtime_paper_faithful_semantics_alignment_",
    "tests/integration/test_runtime_paper_faithful_semantics_alignment_",
    "tests/unit/test_topology_timeout_reward_fidelity_models.py",
)

FORBIDDEN_PATH_PREFIXES = (
    "src/training/",
    "src/agents/",
    "artifacts/",
    "resources/",
    "specs/072-",
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
    "git diff --check",
)

DEFAULT_CHANGED_FILES = (
    "specs/071-runtime-paper-faithful-semantics-alignment/spec.md",
    "specs/071-runtime-paper-faithful-semantics-alignment/plan.md",
    "specs/071-runtime-paper-faithful-semantics-alignment/research.md",
    "specs/071-runtime-paper-faithful-semantics-alignment/data-model.md",
    "specs/071-runtime-paper-faithful-semantics-alignment/tasks.md",
    "specs/071-runtime-paper-faithful-semantics-alignment/quickstart.md",
    "specs/071-runtime-paper-faithful-semantics-alignment/checklists/requirements.md",
    "specs/071-runtime-paper-faithful-semantics-alignment/contracts/runtime-paper-faithful-semantics-report-schema.md",
    "specs/071-runtime-paper-faithful-semantics-alignment/implementation-prompt.md",
    "src/analysis/runtime_paper_faithful_semantics_alignment/__init__.py",
    "src/analysis/runtime_paper_faithful_semantics_alignment/__main__.py",
    "src/analysis/runtime_paper_faithful_semantics_alignment/config.py",
    "src/analysis/runtime_paper_faithful_semantics_alignment/model.py",
    "src/analysis/runtime_paper_faithful_semantics_alignment/report.py",
    "src/analysis/runtime_paper_faithful_semantics_alignment/runner.py",
    "src/environment/paper_timeout.py",
    "src/environment/deadline_rules.py",
    "src/environment/reward_timing.py",
    "tests/unit/test_topology_timeout_reward_fidelity_models.py",
    "tests/unit/test_runtime_paper_faithful_semantics_alignment_deadline.py",
    "tests/unit/test_runtime_paper_faithful_semantics_alignment_reward.py",
    "tests/unit/test_runtime_paper_faithful_semantics_alignment_report.py",
    "tests/unit/test_runtime_paper_faithful_semantics_alignment_scope_guard.py",
    "tests/integration/test_runtime_paper_faithful_semantics_alignment_report.py",
    "tests/unit/test_topology_timeout_reward_fidelity_models.py",
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
    output = _git_output("diff", "--name-only", f"{BASE_FEATURE_070_COMMIT}...HEAD")
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
        raise RuntimeError("Dirty or diff paths outside approved Feature 071 scope: " + ", ".join(sorted(set(forbidden))))
    return checked
