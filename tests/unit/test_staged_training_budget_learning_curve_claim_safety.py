from __future__ import annotations

import unittest

from src.analysis.staged_training_budget_learning_curve.model import StagedTrainingBudgetLearningCurveReport

from tests.unit.test_staged_training_budget_learning_curve_schema import _base_report_kwargs


class StagedTrainingBudgetLearningCurveClaimSafetyTests(unittest.TestCase):
    def test_blocked_report_can_exist_without_pass_claims(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["final_verdict"] = "claim_safety_blocked"
        kwargs["remaining_blockers"] = ["claim_safety_blocked"]
        kwargs["claim_safety_status"] = {
            "paper_reproduction_claim_made": True,
            "performance_superiority_claim_made": False,
            "baseline_superiority_claim_made": False,
            "claim_safety_passed": False,
        }
        report = StagedTrainingBudgetLearningCurveReport(**kwargs)
        self.assertEqual(report.final_verdict, "claim_safety_blocked")

    def test_ready_report_rejects_paper_reproduction_claim(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["claim_safety_status"]["paper_reproduction_claim_made"] = True
        with self.assertRaises(ValueError):
            StagedTrainingBudgetLearningCurveReport(**kwargs)

    def test_ready_report_rejects_baseline_superiority_claim(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["claim_safety_status"]["baseline_superiority_claim_made"] = True
        with self.assertRaises(ValueError):
            StagedTrainingBudgetLearningCurveReport(**kwargs)


if __name__ == "__main__":
    unittest.main()
