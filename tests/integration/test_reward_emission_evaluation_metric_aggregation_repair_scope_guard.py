from __future__ import annotations

import unittest

from src.analysis.reward_emission_evaluation_metric_aggregation_repair.diagnostics import git_status_paths


ALLOWED_PREFIXES = (
    "artifacts/analysis/reward-emission-evaluation-metric-aggregation-repair/",
    "docs/architecture/euls_phase25_reward_emission_evaluation_metric_aggregation_repair.md",
    "specs/066-reward-emission-evaluation-metric-aggregation-repair/",
    "src/analysis/reward_emission_evaluation_metric_aggregation_repair/",
    "tests/unit/test_reward_emission_evaluation_metric_aggregation_repair",
    "tests/integration/test_reward_emission_evaluation_metric_aggregation_repair",
)

FORBIDDEN_PREFIXES = (
    "src/environment/",
    "src/dal/",
    "src/policies/",
    "src/environment/reward_timing.py",
    "src/environment/replay_hash.py",
    "src/analysis/staged_training_budget_learning_curve/",
    "src/analysis/final_review_release_gate_batch/",
    "requirements",
    "pyproject.toml",
    "poetry.lock",
    "uv.lock",
    "AGENTS.md",
    ".specify/feature.json",
)


class RewardEmissionEvaluationMetricAggregationRepairScopeGuardTests(unittest.TestCase):
    def test_no_forbidden_paths_are_modified(self) -> None:
        status_paths = git_status_paths()
        self.assertTrue(status_paths)
        self.assertFalse(any(path.startswith(FORBIDDEN_PREFIXES) for path in status_paths), status_paths)
        self.assertTrue(
            all(
                path.startswith(ALLOWED_PREFIXES)
                for path in status_paths
                if path.startswith("src/analysis/reward_emission_evaluation_metric_aggregation_repair/")
                or path.startswith("tests/unit/test_reward_emission_evaluation_metric_aggregation_repair")
                or path.startswith("tests/integration/test_reward_emission_evaluation_metric_aggregation_repair")
            ),
            status_paths,
        )


if __name__ == "__main__":
    unittest.main()
