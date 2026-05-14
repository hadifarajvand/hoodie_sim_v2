from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ALLOWED_PREFIXES = (
    "specs/038-training-foundation-contract/",
    "src/analysis/training_foundation_contract/",
    "tests/unit/test_training_foundation_contract.py",
    "tests/integration/test_training_foundation_contract_report.py",
    "tests/integration/test_training_readiness_gate.py",
    "tests/integration/test_training_foundation_scope_guard.py",
    "artifacts/analysis/training-foundation-contract/",
)

FORBIDDEN_PREFIXES = (
    "requirements",
    "pyproject.toml",
    "poetry.lock",
    "Pipfile",
    "Pipfile.lock",
    "environment",
    "setup.py",
    "setup.cfg",
    "src/environment/",
    "src/policies/",
    "src/training/",
    "src/models/",
    "src/agents/",
    "src/learning/",
    "src/replay/",
    "src/memory/",
    "src/campaigns/",
    "artifacts/campaigns/",
    "resources/papers/",
    "artifacts/analysis/user-approved-assumption-patch-registry/",
    "artifacts/analysis/runtime-adoption-approved-assumption-registry/",
    "artifacts/analysis/baseline-revalidation-after-runtime-repair/",
)


class TrainingFoundationScopeGuardIntegrationTests(unittest.TestCase):
    def _git_status_paths(self) -> list[str]:
        result = subprocess.run(["git", "status", "--short"], check=True, capture_output=True, text=True)
        paths: list[str] = []
        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            paths.append(line[3:].strip())
        return paths

    def test_no_dependency_environment_policy_reward_runtime_drift(self) -> None:
        modified_paths = self._git_status_paths()
        forbidden_hits = [path for path in modified_paths if path.startswith(FORBIDDEN_PREFIXES)]
        self.assertEqual(forbidden_hits, [])
        self.assertTrue(any(path.startswith("specs/038-training-foundation-contract/") for path in modified_paths))
        self.assertTrue(all(path.startswith(ALLOWED_PREFIXES) or path.startswith("specs/038-training-foundation-contract/") for path in modified_paths))

    def test_no_training_or_neural_network_code_added(self) -> None:
        package_root = Path("src/analysis/training_foundation_contract")
        self.assertTrue(package_root.exists())
        self.assertTrue((package_root / "__init__.py").exists())
        self.assertTrue((package_root / "report.py").exists())
        source = (package_root / "report.py").read_text(encoding="utf-8")
        self.assertNotRegex(source, r"(?m)^\s*(import|from)\s+torch\b")
        self.assertNotRegex(source, r"(?m)^\s*(import|from)\s+(torchvision|torchaudio|torchrl)\b")
        self.assertNotRegex(source, r"(?m)\bnn\.\w+")
        self.assertNotRegex(source, r"(?m)\boptimizer\b")
        self.assertNotRegex(source, r"(?m)\breplay buffer\b")
        self.assertNotRegex(source, r"(?m)\btraining loop\b")


if __name__ == "__main__":
    unittest.main()
