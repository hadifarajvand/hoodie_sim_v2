from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Sequence


FEATURE_ID = "076-combined-baseline-proposed-comparative-readiness"
FEATURE_NAME = "Feature 076 - Combined Baseline + Proposed Comparative Readiness"
READY_STATUS = "combined_baseline_proposed_comparative_readiness_ready"
BLOCKED_STATUS = "combined_baseline_proposed_comparative_readiness_with_blockers"
IMPLEMENTATION_BRANCH = "076-combined-baseline-proposed-comparative-readiness"
BASE_FEATURE_075_COMMIT = "b23b2fa5b1c8fc6d58f3eb533164f83c05c2ec61"

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

ALLOWED_PATH_PATTERNS: tuple[str, ...] = (
    "specs/076-combined-baseline-proposed-comparative-readiness/",
    "src/analysis/combined_baseline_proposed_comparative_readiness/",
    "tests/unit/test_combined_baseline_proposed_comparative_readiness_",
    "tests/integration/test_combined_baseline_proposed_comparative_readiness_",
)

FORBIDDEN_PATH_PATTERNS: tuple[str, ...] = (
    "src/environment/",
    "src/policies/",
    "src/training/",
    "src/agents/",
    "artifacts/",
    "resources/",
    "specs/077-",
    "src/analysis/end_to_end_hoodie_golden_trace_validation/",
    "src/analysis/runtime_paper_faithful_semantics_alignment/",
    "src/analysis/controlled_evaluation_batch_readiness/",
    "src/analysis/topology_timeout_reward_fidelity/",
    "src/analysis/full_hoodie_mechanism_fidelity_batch/",
    "src/analysis/baseline_policy_comparative_evaluation_readiness/",
    "src/analysis/proposed_method_integration_readiness/",
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

DEFAULT_OUTPUT_DIR = Path("artifacts/analysis/combined_baseline_proposed_comparative_readiness")

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
    "src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_combined_baseline_proposed_comparative_readiness_*.py'",
    "src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_combined_baseline_proposed_comparative_readiness_*.py'",
    "git diff --check",
)

DEFAULT_CHANGED_FILES = (
    "specs/076-combined-baseline-proposed-comparative-readiness/spec.md",
    "specs/076-combined-baseline-proposed-comparative-readiness/plan.md",
    "specs/076-combined-baseline-proposed-comparative-readiness/data-model.md",
    "specs/076-combined-baseline-proposed-comparative-readiness/research.md",
    "specs/076-combined-baseline-proposed-comparative-readiness/quickstart.md",
    "specs/076-combined-baseline-proposed-comparative-readiness/tasks.md",
    "specs/076-combined-baseline-proposed-comparative-readiness/checklists/requirements.md",
    "specs/076-combined-baseline-proposed-comparative-readiness/contracts/combined-comparative-report-schema.md",
    "specs/076-combined-baseline-proposed-comparative-readiness/contracts/validation-rules.md",
    "src/analysis/combined_baseline_proposed_comparative_readiness/__init__.py",
    "src/analysis/combined_baseline_proposed_comparative_readiness/__main__.py",
    "src/analysis/combined_baseline_proposed_comparative_readiness/config.py",
    "src/analysis/combined_baseline_proposed_comparative_readiness/model.py",
    "src/analysis/combined_baseline_proposed_comparative_readiness/report.py",
    "src/analysis/combined_baseline_proposed_comparative_readiness/runner.py",
    "tests/unit/test_combined_baseline_proposed_comparative_readiness_model.py",
    "tests/unit/test_combined_baseline_proposed_comparative_readiness_report.py",
    "tests/unit/test_combined_baseline_proposed_comparative_readiness_scope_guard.py",
    "tests/integration/test_combined_baseline_proposed_comparative_readiness_report.py",
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
    output = _git_output("diff", "--name-only", f"{BASE_FEATURE_075_COMMIT}...HEAD")
    return [line for line in output.splitlines() if line]


def _all_paths() -> list[str]:
    return [*_tracked_paths(), *_staged_paths(), *_diff_paths()]


def _is_allowed(path: str) -> bool:
    if not path:
        return True
    if Path(path).name in DEPENDENCY_FILE_NAMES:
        return False
    if path.startswith("src/analysis/") and not path.startswith("src/analysis/combined_baseline_proposed_comparative_readiness/"):
        return False
    if any(path.startswith(prefix) for prefix in FORBIDDEN_PATH_PATTERNS):
        return False
    return any(path.startswith(prefix) for prefix in ALLOWED_PATH_PATTERNS)


def validate_scope(paths: Sequence[str] | None = None) -> list[str]:
    checked = list(paths) if paths is not None else _all_paths()
    forbidden = [path for path in checked if path and not _is_allowed(path)]
    if forbidden:
        raise RuntimeError("Dirty or diff paths outside approved Feature 076 scope: " + ", ".join(sorted(set(forbidden))))
    return checked
