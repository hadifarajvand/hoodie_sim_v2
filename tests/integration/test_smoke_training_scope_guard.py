from __future__ import annotations

import subprocess
import unittest


ALLOWED_COMMITTED_PREFIXES = (
    "specs/040-smoke-training/",
    "src/analysis/smoke_training/",
    "tests/unit/test_smoke_training_contract.py",
    "tests/integration/test_smoke_training_report.py",
    "tests/integration/test_smoke_training_determinism.py",
    "tests/integration/test_smoke_training_scope_guard.py",
    "tests/unit/test_paper_hoodie_network_config.py",
    "tests/unit/test_paper_hoodie_network_shapes.py",
    "tests/integration/test_paper_hoodie_network_report.py",
    "tests/integration/test_paper_hoodie_network_scope_guard.py",
    "tests/unit/test_training_foundation_contract.py",
    "tests/integration/test_training_foundation_contract_report.py",
    "tests/integration/test_training_readiness_gate.py",
    "artifacts/analysis/smoke-training/",
)


class SmokeTrainingScopeGuardIntegrationTests(unittest.TestCase):
    def _git_diff_paths(self) -> list[str]:
        result = subprocess.run(["git", "diff", "--name-only", "main...HEAD"], check=True, capture_output=True, text=True)
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    def _git_cached_paths(self) -> list[str]:
        result = subprocess.run(["git", "diff", "--cached", "--name-only"], check=True, capture_output=True, text=True)
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    def test_no_full_training_campaign_or_target_update_in_committed_scope(self) -> None:
        for path in self._git_diff_paths():
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

    def test_no_dependency_environment_policy_reward_drift(self) -> None:
        for path in self._git_cached_paths():
            self.assertNotEqual(path, ".specify/feature.json")
            self.assertNotIn("requirements.txt", path)


if __name__ == "__main__":
    unittest.main()
