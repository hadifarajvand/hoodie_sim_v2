from __future__ import annotations

import unittest
from unittest import mock

from src.analysis.staged_training_budget_learning_curve.runner import build_staged_training_budget_learning_curve_report

from tests.unit.test_staged_training_budget_learning_curve_schema import _base_report_kwargs, _base_checkpoint_metrics


def _mock_execution() -> dict[str, object]:
    checkpoint_metrics = _base_checkpoint_metrics()
    return {
        "training_mode": "cumulative_staged",
        "checkpoint_metrics": checkpoint_metrics,
        "loss_values": [metric["last_loss"] for metric in checkpoint_metrics],
        "baseline_reference_summary": {
            "available": True,
            "artifact_path": "artifacts/analysis/full-paper-default-training-campaign-execution/baseline-evaluation-metrics.json",
            "baseline_policy_names": ["local-only", "random-legal", "fixed-horizontal"],
            "evaluated_policy_count": 3,
            "actual_baseline_evaluation_episode_count": 100,
            "baseline_metrics_real_execution": True,
            "no_baseline_superiority_claim": True,
        },
        "comparison_ready": True,
        "optimizer_step_count": 50,
        "replay_size": 500,
    }


class StagedTrainingBudgetLearningCurveMetricsTests(unittest.TestCase):
    def test_checkpoint_action_accounting_reconciles(self) -> None:
        with mock.patch("src.analysis.staged_training_budget_learning_curve.runner._build_cumulative_training_sweep", return_value=_mock_execution()), \
            mock.patch("src.analysis.staged_training_budget_learning_curve.runner._feature_062_prerequisite_verified", return_value={"path": "feature062", "exists": True, "verified": True, "final_verdict": "unified_campaign_result_analysis_ready", "remaining_blockers": []}), \
            mock.patch("src.analysis.staged_training_budget_learning_curve.runner._baseline_reference_summary", return_value=_mock_execution()["baseline_reference_summary"]), \
            mock.patch("src.analysis.staged_training_budget_learning_curve.runner.generate_figures", return_value={
                "figures_generated": True,
                "figure_count": 5,
                "figure_files": [
                    "figure_01_eval_reward_by_training_budget.png",
                    "figure_02_replay_size_and_optimizer_steps_by_budget.png",
                    "figure_03_action_distribution_by_training_budget.png",
                    "figure_04_loss_by_training_budget.png",
                    "figure_05_comparison_readiness_by_budget.png",
                ],
                "figure_directory": "artifacts/analysis/staged-training-budget-learning-curve/figures",
                "paper_reproduction_figures": False,
            }):
            report = build_staged_training_budget_learning_curve_report()

        payload = report.to_dict()
        self.assertEqual(payload["checkpoint_budgets"], [100, 150, 200, 500])
        self.assertTrue(payload["comparison_readiness_summary"]["comparison_ready"])
        self.assertTrue(payload["figure_manifest"]["figures_generated"])
        for checkpoint in payload["checkpoint_metrics"]:
            self.assertTrue(checkpoint["action_accounting_reconciled"])
            self.assertEqual(checkpoint["action_count_total"], checkpoint["replay_size"])
            self.assertTrue(checkpoint["loss_finite"])
            self.assertEqual(checkpoint["evaluation_reward_summary"]["evaluation_episode_count"], 100)
            self.assertTrue(checkpoint["comparison_ready"])
            self.assertTrue(checkpoint["claim_safety_status"]["claim_safety_passed"])

    def test_report_uses_cumulative_training_mode(self) -> None:
        with mock.patch("src.analysis.staged_training_budget_learning_curve.runner._build_cumulative_training_sweep", return_value=_mock_execution()), \
            mock.patch("src.analysis.staged_training_budget_learning_curve.runner._feature_062_prerequisite_verified", return_value={"path": "feature062", "exists": True, "verified": True, "final_verdict": "unified_campaign_result_analysis_ready", "remaining_blockers": []}), \
            mock.patch("src.analysis.staged_training_budget_learning_curve.runner._baseline_reference_summary", return_value=_mock_execution()["baseline_reference_summary"]), \
            mock.patch("src.analysis.staged_training_budget_learning_curve.runner.generate_figures", return_value={
                "figures_generated": True,
                "figure_count": 5,
                "figure_files": [
                    "figure_01_eval_reward_by_training_budget.png",
                    "figure_02_replay_size_and_optimizer_steps_by_budget.png",
                    "figure_03_action_distribution_by_training_budget.png",
                    "figure_04_loss_by_training_budget.png",
                    "figure_05_comparison_readiness_by_budget.png",
                ],
                "figure_directory": "artifacts/analysis/staged-training-budget-learning-curve/figures",
                "paper_reproduction_figures": False,
            }):
            report = build_staged_training_budget_learning_curve_report()

        payload = report.to_dict()
        self.assertEqual(payload["training_mode"], "cumulative_staged")
        self.assertFalse(payload["training_rerun_from_scratch"])
        self.assertEqual(payload["total_max_training_budget"], 500)


if __name__ == "__main__":
    unittest.main()
