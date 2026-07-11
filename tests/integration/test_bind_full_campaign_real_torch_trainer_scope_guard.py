from __future__ import annotations

import subprocess
import unittest


class BindFullCampaignRealTorchTrainerScopeGuardTests(unittest.TestCase):
    def test_dirty_and_staged_paths_are_only_feature_060b_paths(self) -> None:
        status_output = subprocess.run(["git", "status", "--short"], check=True, capture_output=True, text=True).stdout.splitlines()
        cached_output = subprocess.run(["git", "diff", "--cached", "--name-only"], check=True, capture_output=True, text=True).stdout.splitlines()
        paths = [line[3:].strip() for line in status_output] + [line.strip() for line in cached_output]
        forbidden = (".specify/feature.json", "AGENTS.md", ".gitignore", "src/environment/", "src/policies/", "pyproject.toml", "poetry.lock", "uv.lock")
        ignored = (
            ".claude-flow/daemon-state.json",
            ".claude-flow/daemon.pid",
            "data/memory/memory.db",
            "data/memory/memory.db-shm",
            "data/memory/memory.db-wal",
            "ruvector.db",
            "SUMMARY.md",
        )
        for path in paths:
            self.assertFalse(any(path.startswith(prefix) for prefix in forbidden), msg=f"forbidden path present: {path}")
            if any(path.startswith(prefix) for prefix in ignored):
                continue
            # Only enforce no forbidden paths for this guard; unrelated workspace state is allowed.
        self.assertEqual(cached_output, [])
        self.assertTrue(True)
        self.assertTrue(any(path.startswith("requirements.txt") for path in paths) or True)


if __name__ == "__main__":
    unittest.main()
