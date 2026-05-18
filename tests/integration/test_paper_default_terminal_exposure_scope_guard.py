from __future__ import annotations

import subprocess
import unittest


ALLOWED_COMMITTED_PREFIXES = (
    "specs/042-paper-default-terminal-exposure-probe/",
    "src/analysis/paper_default_terminal_exposure_probe/",
    "tests/unit/test_paper_default_terminal_exposure_config.py",
    "tests/unit/test_paper_default_terminal_exposure_schema.py",
    "tests/integration/test_paper_default_terminal_exposure_probe.py",
    "tests/integration/test_paper_default_terminal_exposure_report.py",
    "tests/integration/test_paper_default_terminal_exposure_scope_guard.py",
    "artifacts/analysis/paper-default-terminal-exposure-probe/",
)


class PaperDefaultTerminalExposureScopeGuardIntegrationTests(unittest.TestCase):
    def _git_diff_paths(self) -> list[str]:
        result = subprocess.run(["git", "diff", "--name-only", "main...HEAD"], check=True, capture_output=True, text=True)
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    def _git_cached_paths(self) -> list[str]:
        result = subprocess.run(["git", "diff", "--cached", "--name-only"], check=True, capture_output=True, text=True)
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    def test_no_training_optimizer_replay_target_update_execution_added(self) -> None:
        for path in self._git_diff_paths():
            self.assertTrue(path.startswith(ALLOWED_COMMITTED_PREFIXES), path)
            self.assertNotEqual(path, ".specify/feature.json")
            self.assertFalse(path.startswith("src/environment/"), path)
            self.assertFalse(path.startswith("src/policies/"), path)

    def test_no_dependency_environment_policy_reward_drift(self) -> None:
        for path in self._git_cached_paths():
            self.assertNotEqual(path, ".specify/feature.json")


if __name__ == "__main__":
    unittest.main()
