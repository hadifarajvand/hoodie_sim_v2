from __future__ import annotations

import subprocess
import unittest


FORBIDDEN_PATH_PREFIXES = (
    "src/policies/",
    "src/metrics/",
    "src/training/",
    "configs/",
    "dependency",
    "requirements",
    "poetry.lock",
    "Pipfile.lock",
    "uv.lock",
    "artifacts/campaign",
)


class EnvironmentLifecycleFinalDiffIntegrationTest(unittest.TestCase):
    def test_no_forbidden_paths_changed(self) -> None:
        changed_paths = [
            line[3:]
            for line in subprocess.run(
                ["git", "status", "--short", "--untracked-files=normal"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.splitlines()
            if len(line) > 3
        ]
        for path in changed_paths:
            for forbidden in FORBIDDEN_PATH_PREFIXES:
                self.assertFalse(
                    path.startswith(forbidden) or forbidden in path,
                    f"forbidden path changed: {path}",
                )


if __name__ == "__main__":
    unittest.main()
