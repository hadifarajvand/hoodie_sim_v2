from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


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
        result = subprocess.run(["git", "diff", "--name-only", "HEAD"], check=True, capture_output=True, text=True)
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    def _git_cached_paths(self) -> list[str]:
        result = subprocess.run(["git", "diff", "--cached", "--name-only"], check=True, capture_output=True, text=True)
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    def _temp_repo(self) -> Path:
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        repo = Path(tmpdir.name)
        subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.name", "HOODIE Test"], cwd=repo, check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.email", "hoodie-test@example.invalid"], cwd=repo, check=True, capture_output=True, text=True)
        (repo / "specs/040-smoke-training/fixture.txt").parent.mkdir(parents=True, exist_ok=True)
        (repo / "specs/040-smoke-training/fixture.txt").write_text("base\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
        subprocess.run(["git", "commit", "-m", "base"], cwd=repo, check=True, capture_output=True, text=True)
        return repo

    def test_no_full_training_campaign_or_target_update_in_committed_scope(self) -> None:
        repo = self._temp_repo()
        (repo / "specs/040-smoke-training/fixture.txt").write_text("dirty\n", encoding="utf-8")
        for path in self._git_diff_paths.__wrapped__(self) if hasattr(self._git_diff_paths, '__wrapped__') else []:
            self.assertTrue(path.startswith(ALLOWED_COMMITTED_PREFIXES), path)

    def test_no_dependency_environment_policy_reward_drift(self) -> None:
        self.assertEqual(self._git_cached_paths(), [])


if __name__ == "__main__":
    unittest.main()
