from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest import mock

from src.analysis.staged_training_budget_learning_curve.config import (
    CHECKPOINT_METRICS_JSON,
    COMPARISON_READINESS_JSON,
    FIGURE_MANIFEST_JSON,
    FIGURES_DIR,
    REPORT_JSON,
    REPORT_MD,
    STAGED_COMPARATIVE_TABLE_JSON,
    STAGED_FINDINGS_MD,
)
from src.analysis.staged_training_budget_learning_curve.runner import run_staged_training_budget_learning_curve

from tests.unit.test_staged_training_budget_learning_curve_metrics import _mock_execution


class StagedTrainingBudgetLearningCurveReportIntegrationTests(unittest.TestCase):
    def test_required_artifacts_exist(self) -> None:
        with mock.patch("src.analysis.staged_training_budget_learning_curve.runner._build_cumulative_training_sweep", return_value=_mock_execution()), \
            mock.patch("src.analysis.staged_training_budget_learning_curve.runner._feature_062_prerequisite_verified", return_value={"path": "feature062", "exists": True, "verified": True, "final_verdict": "unified_campaign_result_analysis_ready", "remaining_blockers": []}), \
            mock.patch("src.analysis.staged_training_budget_learning_curve.runner._baseline_reference_summary", return_value=_mock_execution()["baseline_reference_summary"]):
            report = run_staged_training_budget_learning_curve()

        self.assertEqual(report.final_verdict, "staged_training_budget_learning_curve_ready")
        for path in (
            CHECKPOINT_METRICS_JSON,
            COMPARISON_READINESS_JSON,
            STAGED_COMPARATIVE_TABLE_JSON,
            STAGED_FINDINGS_MD,
            FIGURE_MANIFEST_JSON,
            REPORT_JSON,
            REPORT_MD,
        ):
            self.assertTrue(path.exists(), path)
        for figure_name in (
            "figure_01_eval_reward_by_training_budget.png",
            "figure_02_replay_size_and_optimizer_steps_by_budget.png",
            "figure_03_action_distribution_by_training_budget.png",
            "figure_04_loss_by_training_budget.png",
            "figure_05_comparison_readiness_by_budget.png",
        ):
            self.assertTrue((FIGURES_DIR / figure_name).exists())

        payload = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(payload["final_verdict"], "staged_training_budget_learning_curve_ready")
        self.assertTrue(payload["claim_safety_status"]["claim_safety_passed"])


if __name__ == "__main__":
    unittest.main()
