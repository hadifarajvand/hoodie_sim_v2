from __future__ import annotations

import unittest

from src.analysis.hoodie_runtime_evaluation_runner.report import build_feature_085_report


class HoodieRuntimeEvaluationRunnerScopeGuardTests(unittest.TestCase):
    def test_report_claim_boundary_and_scope_proof_reject_forbidden_drift(self) -> None:
        report = build_feature_085_report()
        self.assertEqual(report.feature_id, "085-hoodie-paper-baseline-fidelity-audit")
        claim = " ".join(report.claim_boundary).lower()
        scope = " ".join(report.scope_proof).lower()
        self.assertIn("no statistical superiority", claim)
        self.assertIn("no full empirical paper reproduction", claim)
        self.assertIn("no dcq", scope)
        self.assertIn("no thesis method", scope)
        self.assertIn("no custom queue redesign", scope)
        self.assertIn("no legacy minimum-queue policy remains as an active baseline label", scope)
        self.assertIn("hoodie remains the feature 080 proposed method only", scope)
        self.assertIn("pr #24 remains blocked", scope)


if __name__ == "__main__":
    unittest.main()
