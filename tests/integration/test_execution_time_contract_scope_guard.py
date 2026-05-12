from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


FORBIDDEN_PREFIXES = (
    "src/policies/",
    "src/training/",
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


class ExecutionTimeContractScopeGuardIntegrationTest(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
