from __future__ import annotations

import subprocess
import unittest


ALLOWED_COMMITTED_PREFIXES = (
    "specs/043-task-completion-lifecycle-formula-audit/",
    "src/analysis/task_completion_lifecycle_formula_audit/",
    "tests/unit/test_task_completion_formula_audit.py",
    "tests/unit/test_task_completion_lifecycle_schema.py",
    "tests/integration/test_task_completion_lifecycle_audit.py",
    "tests/integration/test_task_completion_lifecycle_report.py",
    "tests/integration/test_task_completion_lifecycle_scope_guard.py",
    "artifacts/analysis/task-completion-lifecycle-formula-audit/",
)


class TaskCompletionLifecycleScopeGuardIntegrationTests(unittest.TestCase):
    def _git_diff_paths(self) -> list[str]:
        result = subprocess.run(["git", "diff", "--name-only", "main...HEAD"], check=True, capture_output=True, text=True)
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    def _git_cached_paths(self) -> list[str]:
        result = subprocess.run(["git", "diff", "--cached", "--name-only"], check=True, capture_output=True, text=True)
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    def test_scope_is_limited_to_feature_paths(self) -> None:
        for path in self._git_diff_paths():
            self.assertTrue(path.startswith(ALLOWED_COMMITTED_PREFIXES), path)
            self.assertNotEqual(path, ".specify/feature.json")
            self.assertFalse(path.startswith("src/environment/"), path)
            self.assertFalse(path.startswith("src/policies/"), path)
            self.assertFalse(path.endswith("requirements.txt"), path)
            self.assertFalse(path.endswith("pyproject.toml"), path)

    def test_feature_json_must_not_be_staged(self) -> None:
        for path in self._git_cached_paths():
            self.assertNotEqual(path, ".specify/feature.json")


if __name__ == "__main__":
    unittest.main()
