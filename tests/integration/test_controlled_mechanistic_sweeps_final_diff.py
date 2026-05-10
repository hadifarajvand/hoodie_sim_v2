from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


class ControlledMechanisticSweepsFinalDiffTests(unittest.TestCase):
    def test_final_diff_stays_within_allowed_paths(self) -> None:
        diff = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        untracked = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        changed_paths = [Path(item) for item in diff + untracked]
        forbidden_tokens = (
            "src/environment/",
            "src/policies/",
            "src/training/",
            "src/metrics/",
            "campaign/",
            ".tf",
            ".lock",
            "plot",
        )
        for path in changed_paths:
            self.assertFalse(
                any(token in path.as_posix() for token in forbidden_tokens),
                msg=f"Forbidden path touched: {path}",
            )


if __name__ == "__main__":
    unittest.main()
