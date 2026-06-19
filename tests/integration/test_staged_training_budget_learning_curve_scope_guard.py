from __future__ import annotations

import subprocess
import unittest


APPROVED_PATH_PREFIXES = (
    "artifacts/analysis/staged-training-budget-learning-curve/",
    "docs/architecture/euls_phase22_staged_training_budget_learning_curve.md",
    "specs/063-staged-training-budget-learning-curve/",
    "src/analysis/staged_training_budget_learning_curve/",
    "tests/unit/test_staged_training_budget_learning_curve",
    "tests/integration/test_staged_training_budget_learning_curve",
)

FORBIDDEN_PATH_PREFIXES = (
    "src/environment/",
    "src/dal/",
    "src/policies/",
    "src/environment/replay_hash.py",
    "src/analysis/full_training_reproduction_campaign/",
    "src/analysis/full_paper_default_training_campaign_execution/",
    "src/analysis/unified_campaign_result_analysis_figures_findings/",
    "requirements",
    "pyproject.toml",
    "poetry.lock",
    "uv.lock",
    "AGENTS.md",
    ".specify/feature.json",
)


def _git_output(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


class StagedTrainingBudgetLearningCurveScopeGuardTests(unittest.TestCase):
    def test_forbidden_paths_are_not_modified(self) -> None:
        status_paths = [line[3:].strip() for line in _git_output("status", "--short").splitlines() if line.strip()]
        diff_paths = [line for line in _git_output("diff", "--name-only").splitlines() if line]
        staged_paths = [line for line in _git_output("diff", "--cached", "--name-only").splitlines() if line]
        paths = status_paths + diff_paths + staged_paths
        candidate_paths = [
            path
            for path in paths
            if path.startswith(APPROVED_PATH_PREFIXES) or path.startswith(FORBIDDEN_PATH_PREFIXES)
        ]
        self.assertTrue(candidate_paths)
        self.assertTrue(all(path.startswith(APPROVED_PATH_PREFIXES) for path in candidate_paths))
        self.assertFalse(any(path.startswith(FORBIDDEN_PATH_PREFIXES) for path in candidate_paths))


if __name__ == "__main__":
    unittest.main()
