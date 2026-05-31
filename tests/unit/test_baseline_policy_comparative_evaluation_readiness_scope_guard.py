from __future__ import annotations

import unittest

from src.analysis.baseline_policy_comparative_evaluation_readiness.config import validate_scope


class BaselinePolicyComparativeEvaluationReadinessScopeGuardTests(unittest.TestCase):
    def test_validate_scope_allows_only_feature_074_paths(self) -> None:
        allowed = validate_scope(
            [
                "specs/074-baseline-policy-comparative-evaluation-readiness/tasks.md",
                "src/analysis/baseline_policy_comparative_evaluation_readiness/report.py",
                "tests/unit/test_baseline_policy_comparative_evaluation_readiness_report.py",
            ]
        )
        self.assertEqual(
            allowed,
            [
                "specs/074-baseline-policy-comparative-evaluation-readiness/tasks.md",
                "src/analysis/baseline_policy_comparative_evaluation_readiness/report.py",
                "tests/unit/test_baseline_policy_comparative_evaluation_readiness_report.py",
            ],
        )

    def test_validate_scope_rejects_feature_075_and_forbidden_paths(self) -> None:
        with self.assertRaises(RuntimeError):
            validate_scope(
                [
                    "specs/075-proposed-deadline-aware-method-integration-readiness/spec.md",
                    "src/training/runner.py",
                ]
            )


if __name__ == "__main__":
    unittest.main()
