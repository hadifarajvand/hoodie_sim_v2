from __future__ import annotations

import unittest

from src.analysis.controlled_evaluation_batch_readiness.config import validate_scope


class ControlledEvaluationBatchReadinessScopeGuardTests(unittest.TestCase):
    def test_validate_scope_allows_only_feature_073_paths(self) -> None:
        allowed = validate_scope(
            [
                "specs/073-controlled-evaluation-batch-readiness/tasks.md",
                "src/analysis/controlled_evaluation_batch_readiness/report.py",
                "tests/unit/test_controlled_evaluation_batch_readiness_report.py",
            ]
        )
        self.assertEqual(
            allowed,
            [
                "specs/073-controlled-evaluation-batch-readiness/tasks.md",
                "src/analysis/controlled_evaluation_batch_readiness/report.py",
                "tests/unit/test_controlled_evaluation_batch_readiness_report.py",
            ],
        )

    def test_validate_scope_rejects_feature_074_and_forbidden_paths(self) -> None:
        with self.assertRaises(RuntimeError):
            validate_scope(
                [
                    "specs/074-baseline-policy-comparative-evaluation-readiness/spec.md",
                    "src/training/runner.py",
                ]
            )

