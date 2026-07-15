from __future__ import annotations

import unittest

from src.analysis.git_base_ref import git_triple_dot_range
from tests.helpers.git_repo import make_temp_git_repo


class PaperDefaultPilotTrainingRunScopeGuardTests(unittest.TestCase):
    def test_git_status_and_diff_only_show_feature_057_paths(self) -> None:
        repo = make_temp_git_repo()
        self.addCleanup(repo.cleanup)
        repo.commit_file("base.txt", "base\n", "base commit")
        repo.git("checkout", "-b", "feature")
        repo.write("artifacts/analysis/paper-default-pilot-training-run/report.json", "{}\n")
        repo.write("specs/057-paper-default-pilot-training-run/spec.md", "feature\n")
        repo.git("add", "artifacts/analysis/paper-default-pilot-training-run/report.json", "specs/057-paper-default-pilot-training-run/spec.md")
        repo.git("commit", "-m", "feature commit")
        status_output = repo.output("status", "--short").splitlines()
        diff_output = repo.output("diff", "--name-only", git_triple_dot_range(repo.root)).splitlines()
        cached_output = repo.output("diff", "--cached", "--name-only").splitlines()

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
