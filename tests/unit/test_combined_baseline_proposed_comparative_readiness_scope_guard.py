from __future__ import annotations

import unittest

from src.analysis.combined_baseline_proposed_comparative_readiness.config import validate_scope


class CombinedBaselineProposedComparativeReadinessScopeGuardTests(unittest.TestCase):
    def test_validate_scope_allows_only_feature_076_paths(self) -> None:
        allowed = validate_scope(
            [
                "specs/076-combined-baseline-proposed-comparative-readiness/tasks.md",
                "src/analysis/combined_baseline_proposed_comparative_readiness/report.py",
                "tests/unit/test_combined_baseline_proposed_comparative_readiness_report.py",
            ]
        )
        self.assertEqual(
            allowed,
            [
                "specs/076-combined-baseline-proposed-comparative-readiness/tasks.md",
                "src/analysis/combined_baseline_proposed_comparative_readiness/report.py",
                "tests/unit/test_combined_baseline_proposed_comparative_readiness_report.py",
            ],
        )

    def test_validate_scope_rejects_forbidden_and_feature_077_paths(self) -> None:
        forbidden_paths = [
            "src/environment/paper_timeout.py",
            "src/policies/flc.py",
            "src/training/runner.py",
            "src/agents/worker.py",
            "requirements.txt",
            "specs/077-next-feature/spec.md",
        ]
        with self.assertRaises(RuntimeError):
            validate_scope(forbidden_paths)


if __name__ == "__main__":
    unittest.main()
