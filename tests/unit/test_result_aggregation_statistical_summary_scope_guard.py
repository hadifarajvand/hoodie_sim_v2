from __future__ import annotations

import unittest

from src.analysis.result_aggregation_statistical_summary.config import validate_scope


class ResultAggregationStatisticalSummaryScopeGuardTests(unittest.TestCase):
    def test_allowed_package_path_passes(self) -> None:
        self.assertEqual(
            validate_scope(["src/analysis/result_aggregation_statistical_summary/report.py"]),
            ["src/analysis/result_aggregation_statistical_summary/report.py"],
        )

    def test_allowed_test_path_passes(self) -> None:
        self.assertEqual(
            validate_scope(["tests/unit/test_result_aggregation_statistical_summary_report.py"]),
            ["tests/unit/test_result_aggregation_statistical_summary_report.py"],
        )

    def test_forbidden_environment_path_fails(self) -> None:
        with self.assertRaises(ValueError):
            validate_scope(["src/environment/paper_timeout.py"])

    def test_forbidden_policies_path_fails(self) -> None:
        with self.assertRaises(ValueError):
            validate_scope(["src/policies/common.py"])

    def test_forbidden_training_path_fails(self) -> None:
        with self.assertRaises(ValueError):
            validate_scope(["src/training/launch.py"])

    def test_forbidden_artifacts_path_fails(self) -> None:
        with self.assertRaises(ValueError):
            validate_scope(["artifacts/result.json"])

    def test_forbidden_future_feature_path_fails(self) -> None:
        with self.assertRaises(ValueError):
            validate_scope(["src/analysis/result_aggregation_080/report.py"])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
