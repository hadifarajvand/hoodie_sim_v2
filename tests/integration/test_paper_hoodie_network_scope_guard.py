from __future__ import annotations

import subprocess
import unittest


ALLOWED_COMMITTED_PREFIXES = (
    "specs/039-paper-hoodie-network-implementation/",
    "src/analysis/paper_hoodie_network_implementation/",
    "tests/unit/test_paper_hoodie_network_config.py",
    "tests/unit/test_paper_hoodie_network_shapes.py",
    "tests/integration/test_paper_hoodie_network_report.py",
    "tests/integration/test_paper_hoodie_network_scope_guard.py",
    "artifacts/analysis/paper-hoodie-network-implementation/",
)


class PaperHoodieNetworkScopeGuardIntegrationTests(unittest.TestCase):
    def _git_status_paths(self) -> list[str]:
        result = subprocess.run(["git", "status", "--short"], check=True, capture_output=True, text=True)
        paths: list[str] = []
        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            paths.append(line[3:].strip())
        return paths

    def _git_diff_paths(self) -> list[str]:
        result = subprocess.run(["git", "diff", "--name-only", "main...HEAD"], check=True, capture_output=True, text=True)
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    def test_no_training_optimizer_replay_execution_added(self) -> None:
        diff_paths = self._git_diff_paths()
        for path in diff_paths:
            self.assertTrue(path.startswith(ALLOWED_COMMITTED_PREFIXES), path)
            self.assertNotEqual(path, ".specify/feature.json")

    def test_no_dependency_environment_policy_reward_drift(self) -> None:
        modified_paths = self._git_status_paths()
        for path in modified_paths:
            self.assertTrue(
                path == ".specify/feature.json" or path.startswith(ALLOWED_COMMITTED_PREFIXES),
                path,
            )


if __name__ == "__main__":
    unittest.main()
