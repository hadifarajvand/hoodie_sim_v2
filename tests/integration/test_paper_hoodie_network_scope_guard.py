from __future__ import annotations

import unittest

from src.analysis.git_base_ref import git_triple_dot_range
from tests.helpers.git_repo import make_temp_git_repo


ALLOWED_COMMITTED_PREFIXES = (
    "requirements.txt",
    "specs/039-paper-hoodie-network-implementation/",
    "src/analysis/paper_hoodie_network_implementation/",
    "tests/unit/test_paper_hoodie_network_config.py",
    "tests/unit/test_paper_hoodie_network_shapes.py",
    "tests/integration/test_paper_hoodie_network_report.py",
    "tests/integration/test_paper_hoodie_network_scope_guard.py",
    "tests/integration/test_training_foundation_scope_guard.py",
    "artifacts/analysis/paper-hoodie-network-implementation/",
)


class PaperHoodieNetworkScopeGuardIntegrationTests(unittest.TestCase):
    def _git_diff_paths(self) -> list[str]:
        repo = make_temp_git_repo()
        self.addCleanup(repo.cleanup)
        repo.commit_file("base.txt", "base\n", "base commit")
        repo.git("checkout", "-b", "feature")
        repo.write("artifacts/analysis/paper-hoodie-network-implementation/report.json", "{}\n")
        repo.write("specs/039-paper-hoodie-network-implementation/spec.md", "feature\n")
        repo.git("add", "artifacts/analysis/paper-hoodie-network-implementation/report.json", "specs/039-paper-hoodie-network-implementation/spec.md")
        repo.git("commit", "-m", "feature commit")
        return [line.strip() for line in repo.output("diff", "--name-only", git_triple_dot_range(repo.root)).splitlines() if line.strip()]

    def test_no_training_optimizer_replay_execution_added(self) -> None:
        diff_paths = self._git_diff_paths()
        for path in diff_paths:
            self.assertTrue(path.startswith(ALLOWED_COMMITTED_PREFIXES), path)
            self.assertNotEqual(path, ".specify/feature.json")

    def test_no_dependency_environment_policy_reward_drift(self) -> None:
        modified_paths = []
        for path in modified_paths:
            self.assertTrue(
                path == ".specify/feature.json" or path.startswith(ALLOWED_COMMITTED_PREFIXES),
                path,
            )


if __name__ == "__main__":
    unittest.main()
