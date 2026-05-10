from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


FORBIDDEN_PREFIXES = (
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

ALLOWED_ENV_PATHS = {
    "src/environment/deadline_rules.py",
    "src/environment/environment.py",
    "src/environment/gym_adapter.py",
}


class MechanismRepairScopeGuardIntegrationTest(unittest.TestCase):
    def _changed_paths(self) -> list[str]:
        result = subprocess.run(
            ["git", "status", "--porcelain=v1"],
            check=True,
            capture_output=True,
            text=True,
        )
        paths: list[str] = []
        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            path = line[3:] if len(line) > 3 else line
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            paths.append(path.strip())
        return paths

    def test_no_forbidden_paths_changed(self) -> None:
        changed_paths = self._changed_paths()
        for path in changed_paths:
            normalized = Path(path).as_posix()
            self.assertFalse(
                any(normalized.startswith(prefix) for prefix in FORBIDDEN_PREFIXES),
                msg=f"forbidden path changed: {normalized}",
            )

    def test_environment_touch_surface_is_surgical(self) -> None:
        changed_paths = self._changed_paths()
        env_paths = [Path(path).as_posix() for path in changed_paths if Path(path).as_posix().startswith("src/environment/")]
        self.assertTrue(env_paths, "expected at least one environment path change for the repair")
        self.assertTrue(set(env_paths).issubset(ALLOWED_ENV_PATHS), env_paths)


if __name__ == "__main__":
    unittest.main()
