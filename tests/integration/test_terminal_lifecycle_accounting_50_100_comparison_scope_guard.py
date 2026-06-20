from __future__ import annotations

import unittest

from src.analysis.terminal_lifecycle_accounting_50_100_comparison.config import BRANCH_NAME
from src.analysis.terminal_lifecycle_accounting_50_100_comparison.diagnostics import git_diff_paths, git_status_paths


FORBIDDEN_PREFIXES = (
    "src/environment/",
    "src/dal/",
    "src/policies/",
    "src/environment/reward_timing.py",
    "src/environment/replay_hash.py",
    "src/analysis/staged_training_budget_learning_curve/",
    "src/analysis/final_review_release_gate_batch/",
    "src/analysis/evaluation_instrumentation_reward_state_diagnostic/",
    "src/analysis/reward_emission_evaluation_metric_aggregation_repair/",
    "requirements",
    "pyproject.toml",
    "poetry.lock",
    "uv.lock",
    "AGENTS.md",
    ".specify/feature.json",
)


class TerminalLifecycleAccounting50_100ComparisonScopeGuardTests(unittest.TestCase):
    def test_no_forbidden_paths_are_modified(self) -> None:
        status_paths = git_status_paths()
        diff_paths = git_diff_paths("066-reward-emission-evaluation-metric-aggregation-repair")
        self.assertEqual(BRANCH_NAME, "067-terminal-lifecycle-accounting-50-100-comparison")
        self.assertFalse(any(path.startswith(FORBIDDEN_PREFIXES) for path in status_paths), status_paths)
        self.assertFalse(any(path.startswith(FORBIDDEN_PREFIXES) for path in diff_paths), diff_paths)


if __name__ == "__main__":
    unittest.main()
