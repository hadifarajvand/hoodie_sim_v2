from __future__ import annotations

import unittest

from src.analysis.proposed_method_integration_readiness.config import validate_scope


class ProposedMethodIntegrationReadinessScopeGuardTests(unittest.TestCase):
    def test_validate_scope_allows_only_feature_075_paths(self) -> None:
        allowed = validate_scope(
            [
                "specs/075-proposed-method-integration-readiness/tasks.md",
                "src/analysis/proposed_method_integration_readiness/report.py",
                "tests/unit/test_proposed_method_integration_readiness_report.py",
            ]
        )
        self.assertEqual(
            allowed,
            [
                "specs/075-proposed-method-integration-readiness/tasks.md",
                "src/analysis/proposed_method_integration_readiness/report.py",
                "tests/unit/test_proposed_method_integration_readiness_report.py",
            ],
        )

    def test_validate_scope_rejects_feature_076_and_forbidden_paths(self) -> None:
        with self.assertRaises(RuntimeError):
            validate_scope(
                [
                    "specs/076-proposed-method-final-evaluation/spec.md",
                    "src/training/runner.py",
                ]
            )


if __name__ == "__main__":
    unittest.main()
