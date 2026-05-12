from __future__ import annotations

import subprocess
import unittest


ALLOWED_PREFIXES = (
    "AGENTS.md",
    ".specify/feature.json",
    "src/environment/",
    "src/evaluation/",
    "src/analysis/runtime_adoption_approved_assumption_registry/",
    "artifacts/analysis/runtime-adoption-approved-assumption-registry/",
    "specs/032-runtime-adoption-approved-assumption-registry/",
    "tests/unit/test_compute_config.py",
    "tests/unit/test_runtime_adoption_approved_assumption_registry.py",
    "tests/unit/test_gym_environment.py",
    "tests/integration/test_runtime_adoption_report.py",
    "tests/integration/test_runtime_adoption_scope_guard.py",
    "tests/integration/test_execution_time_flow.py",
    "tests/integration/test_evaluation_runner.py",
)

DISALLOWED_PREFIXES = (
    "src/training/",
    "src/models/",
    "src/policies/",
    "dependencies/",
    "requirements",
    "package.json",
    "poetry.lock",
    "pyproject.toml",
    "configs/",
    "policy/",
    "policies/",
    "campaigns/",
    "baseline/",
    "paper/",
    "resources/papers/hoodie/",
    "artifacts/analysis/user-approved-assumption-patch-registry/",
)


class RuntimeAdoptionScopeGuardIntegrationTests(unittest.TestCase):
    def test_feature_032_scope_guard_no_training_policy_dependency_drift(self) -> None:
        result = subprocess.run(
            ["git", "diff", "--name-only"],
            check=True,
            capture_output=True,
            text=True,
        )
        changed_files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        self.assertTrue(changed_files)
        for path in changed_files:
            self.assertTrue(
                path.startswith(ALLOWED_PREFIXES),
                msg=f"Unexpected changed file: {path}",
            )
            self.assertFalse(
                path.startswith(DISALLOWED_PREFIXES),
                msg=f"Disallowed drift detected: {path}",
            )


if __name__ == "__main__":
    unittest.main()
