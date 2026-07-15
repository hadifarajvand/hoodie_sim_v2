from __future__ import annotations

import unittest

from src.analysis.git_base_ref import git_triple_dot_range
from tests.helpers.git_repo import make_temp_git_repo


ALLOWED_COMMITTED_PREFIXES = (
    "specs/042-paper-default-terminal-exposure-probe/",
    "src/analysis/paper_default_terminal_exposure_probe/",
    "tests/unit/test_paper_default_terminal_exposure_config.py",
    "tests/unit/test_paper_default_terminal_exposure_schema.py",
    "tests/integration/test_paper_default_terminal_exposure_probe.py",
    "tests/integration/test_paper_default_terminal_exposure_report.py",
    "tests/integration/test_paper_default_terminal_exposure_scope_guard.py",
    "artifacts/analysis/paper-default-terminal-exposure-probe/",
    "artifacts/analysis/paper-default-terminal-exposure-report/",
)


class PaperDefaultTerminalExposureScopeGuardIntegrationTests(unittest.TestCase):
    def test_no_training_optimizer_replay_target_update_execution_added(self) -> None:
        repo = make_temp_git_repo()
        self.addCleanup(repo.cleanup)
        repo.commit_file("base.txt", "base\n", "base commit")
        repo.git("checkout", "-b", "feature")
        repo.write("artifacts/analysis/paper-default-terminal-exposure-probe/report.json", "{}\n")
        repo.write("artifacts/analysis/paper-default-terminal-exposure-report/report.json", "{}\n")
        repo.write("specs/042-paper-default-terminal-exposure-probe/spec.md", "feature\n")
        repo.git("add", "artifacts/analysis/paper-default-terminal-exposure-probe/report.json", "artifacts/analysis/paper-default-terminal-exposure-report/report.json", "specs/042-paper-default-terminal-exposure-probe/spec.md")
        repo.git("commit", "-m", "feature commit")
        for path in repo.output("diff", "--name-only", git_triple_dot_range(repo.root)).splitlines():
            self.assertTrue(path.startswith(ALLOWED_COMMITTED_PREFIXES), path)
            self.assertNotEqual(path, ".specify/feature.json")
            self.assertFalse(path.startswith("src/environment/"), path)
            self.assertFalse(path.startswith("src/policies/"), path)

    def test_no_dependency_environment_policy_reward_drift(self) -> None:
        repo = make_temp_git_repo()
        self.addCleanup(repo.cleanup)
        repo.commit_file("base.txt", "base\n", "base commit")
        repo.git("checkout", "-b", "feature")
        repo.write("artifacts/analysis/paper-default-terminal-exposure-report/report.json", "{}\n")
        repo.git("add", "artifacts/analysis/paper-default-terminal-exposure-report/report.json")
        for path in repo.output("diff", "--cached", "--name-only").splitlines():
            self.assertNotEqual(path, ".specify/feature.json")


if __name__ == "__main__":
    unittest.main()
