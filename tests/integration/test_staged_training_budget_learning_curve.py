from __future__ import annotations

import unittest
from unittest import mock

from src.analysis.staged_training_budget_learning_curve.runner import build_staged_training_budget_learning_curve_report

from tests.unit.test_staged_training_budget_learning_curve_metrics import _mock_execution


class StagedTrainingBudgetLearningCurveIntegrationTests(unittest.TestCase):
    def test_runner_generates_ready_report(self) -> None:
        with mock.patch("src.analysis.staged_training_budget_learning_curve.runner._build_cumulative_training_sweep", return_value=_mock_execution()), \
            mock.patch("src.analysis.staged_training_budget_learning_curve.runner._feature_062_prerequisite_verified", return_value={"path": "feature062", "exists": True, "verified": True, "final_verdict": "unified_campaign_result_analysis_ready", "remaining_blockers": []}), \
            mock.patch("src.analysis.staged_training_budget_learning_curve.runner._baseline_reference_summary", return_value=_mock_execution()["baseline_reference_summary"]):
            payload = build_staged_training_budget_learning_curve_report().to_dict()
        self.assertEqual(payload["final_verdict"], "staged_training_budget_learning_curve_ready")
        self.assertEqual(payload["remaining_blockers"], [])
        self.assertTrue(payload["comparison_readiness_summary"]["comparison_ready"])
        self.assertTrue(payload["figure_manifest"]["figures_generated"])
        self.assertEqual(payload["checkpoint_budgets"], [100, 150, 200, 500])


if __name__ == "__main__":
    unittest.main()
