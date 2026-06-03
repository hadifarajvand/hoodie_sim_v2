from __future__ import annotations

import unittest

from src.analysis.hoodie_runtime_evaluation_runner.report import build_feature_082_report


class HoodieRuntimeEvaluationRunnerScopeGuardTests(unittest.TestCase):
    def test_report_claim_boundary_and_scope_proof_reject_forbidden_drift(self) -> None:
        report = build_feature_082_report()
        claim = " ".join(report.claim_boundary).lower()
        scope = " ".join(report.scope_proof).lower()
        self.assertIn("no dcq", claim)
        self.assertIn("no thesis method", claim)
        self.assertIn("no empirical full-paper reproduction", claim)
        self.assertIn("no ranking", scope)
        self.assertIn("no baseline evaluation", scope)
        self.assertIn("no dcq", scope)
        self.assertIn("no thesis method", scope)
        self.assertIn("no statistical superiority", claim)


if __name__ == "__main__":
    unittest.main()
