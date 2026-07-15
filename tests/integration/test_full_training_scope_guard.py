from __future__ import annotations

import unittest

from src.analysis.git_base_ref import git_triple_dot_range
from tests.helpers.git_repo import make_temp_git_repo


ALLOWED_COMMITTED_PREFIXES = (
    "specs/041-full-training-reproduction-campaign/",
    "src/analysis/full_training_reproduction_campaign/",
    "tests/unit/test_full_training_campaign_config.py",
    "tests/unit/test_full_training_replay_contract.py",
    "tests/integration/test_campaign_readiness_gate.py",
    "tests/integration/test_full_training_pilot.py",
    "tests/integration/test_full_training_report.py",
    "tests/integration/test_full_training_scope_guard.py",
    "tests/integration/test_full_training_candidate_gate.py",
    "artifacts/analysis/full-training-reproduction-campaign/",
    "artifacts/checkpoints/full-training-reproduction-campaign/",
)


class FullTrainingScopeGuardIntegrationTests(unittest.TestCase):
    def _git_diff_paths(self) -> list[str]:
        repo = make_temp_git_repo()
        self.addCleanup(repo.cleanup)
        repo.commit_file("base.txt", "base\n", "base commit")
        repo.git("checkout", "-b", "feature")
        repo.write("artifacts/analysis/full-training-reproduction-campaign/report.json", "{}\n")
        repo.write("specs/041-full-training-reproduction-campaign/spec.md", "feature\n")
        repo.git("add", "artifacts/analysis/full-training-reproduction-campaign/report.json", "specs/041-full-training-reproduction-campaign/spec.md")
        repo.git("commit", "-m", "feature commit")
        return [line.strip() for line in repo.output("diff", "--name-only", git_triple_dot_range(repo.root)).splitlines() if line.strip()]

    def _git_cached_paths(self) -> list[str]:
        repo = make_temp_git_repo()
        self.addCleanup(repo.cleanup)
        repo.commit_file("base.txt", "base\n", "base commit")
        repo.git("checkout", "-b", "feature")
        repo.write("artifacts/analysis/full-training-reproduction-campaign/report.json", "{}\n")
        repo.git("add", "artifacts/analysis/full-training-reproduction-campaign/report.json")
        return [line.strip() for line in repo.output("diff", "--cached", "--name-only").splitlines() if line.strip()]

    def test_no_dependency_environment_policy_reward_runtime_drift(self) -> None:
        diff_paths = self._git_diff_paths()
        for path in diff_paths:
            self.assertTrue(path.startswith(ALLOWED_COMMITTED_PREFIXES), path)
            self.assertNotIn(".specify/feature.json", path)
            self.assertNotIn("requirements.txt", path)
            self.assertFalse(path.startswith("src/environment/"), path)
            self.assertFalse(path.startswith("src/policies/"), path)
            self.assertFalse(path.startswith("src/training/"), path)
            self.assertFalse(path.startswith("src/replay/"), path)
            self.assertFalse(path.startswith("src/memory/"), path)
            self.assertFalse(path.startswith("campaign"), path)
            self.assertFalse(path.startswith("resources/papers/"), path)
        self.assertNotIn(
            "artifacts/checkpoints/full-training-reproduction-campaign/pilot_training-checkpoint-metadata.json",
            diff_paths,
        )

    def test_no_dependency_environment_policy_reward_drift_cached(self) -> None:
        for path in self._git_cached_paths():
            self.assertNotEqual(path, ".specify/feature.json")
            self.assertNotIn("requirements.txt", path)


if __name__ == "__main__":
    unittest.main()
