from __future__ import annotations

import subprocess
import unittest


class PaperDefaultPilotTrainingRunScopeGuardTests(unittest.TestCase):
    def test_git_status_and_diff_only_show_feature_057_paths(self) -> None:
        status_output = subprocess.run(["git", "status", "--short"], check=True, capture_output=True, text=True).stdout.splitlines()
        diff_output = subprocess.run(["git", "diff", "--name-only", "main...HEAD"], check=True, capture_output=True, text=True).stdout.splitlines()
        cached_output = subprocess.run(["git", "diff", "--cached", "--name-only"], check=True, capture_output=True, text=True).stdout.splitlines()

        forbidden_prefixes = (
            ".specify/feature.json",
            "AGENTS.md",
            ".gitignore",
            "src/environment/",
            "src/policies/",
            "requirements",
            "pyproject.toml",
            "poetry.lock",
            "uv.lock",
        )
        for line in status_output + diff_output + cached_output:
            path = line[3:].strip() if line.startswith(("??", "M ", "A ", "D ", "R ", "C ", "UU")) else line.strip()
            for forbidden in forbidden_prefixes:
                self.assertFalse(path.startswith(forbidden), msg=f"forbidden path present: {path}")

        approved_prefixes = (
            "artifacts/analysis/paper-default-pilot-training-run/",
            "specs/057-paper-default-pilot-training-run/",
            "src/analysis/paper_default_pilot_training_run/",
            "tests/unit/test_paper_default_pilot_training_run",
            "tests/integration/test_paper_default_pilot_training_run",
        )
        for path in status_output + diff_output + cached_output:
            cleaned = path[3:].strip() if path.startswith(("??", "M ", "A ", "D ", "R ", "C ", "UU")) else path.strip()
            if not cleaned:
                continue
            self.assertTrue(any(cleaned.startswith(prefix) for prefix in approved_prefixes), msg=f"unexpected path: {cleaned}")

        self.assertEqual(cached_output, [])
