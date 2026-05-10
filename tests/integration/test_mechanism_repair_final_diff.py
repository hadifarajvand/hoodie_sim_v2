from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


class MechanismRepairFinalDiffIntegrationTest(unittest.TestCase):
    def test_final_diff_is_limited_to_allowed_repair_surface(self) -> None:
        result = subprocess.run(
            ["git", "status", "--porcelain=v1"],
            check=True,
            capture_output=True,
            text=True,
        )
        changed_paths = []
        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            path = line[3:] if len(line) > 3 else line
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            changed_paths.append(Path(path).as_posix())

        forbidden_prefixes = (
            "src/policies/",
            "src/training/",
            "src/metrics/",
            "campaign",
            "artifacts/campaigns/",
            "poetry.lock",
            "Pipfile.lock",
            "requirements.txt",
            "requirements-dev.txt",
            "uv.lock",
            "package-lock.json",
            "yarn.lock",
            "pnpm-lock.yaml",
        )
        for path in changed_paths:
            self.assertFalse(
                any(path.startswith(prefix) for prefix in forbidden_prefixes),
                msg=f"forbidden path changed: {path}",
            )

        allowed_env_paths = {
            "src/environment/deadline_rules.py",
            "src/environment/environment.py",
            "src/environment/gym_adapter.py",
        }
        env_paths = [path for path in changed_paths if path.startswith("src/environment/")]
        self.assertTrue(env_paths, "expected the timeout/drop repair to touch environment code")
        self.assertTrue(set(env_paths).issubset(allowed_env_paths), env_paths)


if __name__ == "__main__":
    unittest.main()
