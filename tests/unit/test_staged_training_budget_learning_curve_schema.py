from __future__ import annotations

import unittest

from src.analysis.staged_training_budget_learning_curve.model import StagedTrainingBudgetLearningCurveReport


def _base_checkpoint_metrics() -> list[dict[str, object]]:
    budgets = [100, 150, 200, 500]
    return [
        {
            "training_budget": budget,
            "cumulative_training_episode_count": budget,
            "evaluation_episode_count": 100,
            "episode_length": 110,
            "optimizer_step_count": 10 + index,
            "replay_size": 100,
            "action_distribution": {"local": 40, "horizontal": 30, "vertical": 30, "invalid_or_noop_action_count": 0},
            "action_count_total": 100,
            "action_accounting_reconciled": True,
            "loss_count": 3 + index,
            "last_loss": 0.25 + index,
            "loss_finite": True,
            "reward_summary": {"reward_count": 100, "total_reward": -10.0, "mean_reward": -0.1, "pending_at_horizon_count": 0},
            "evaluation_reward_summary": {
                "evaluation_episode_count": 100,
                "mean_reward": -0.1,
                "completed_task_count": 1,
                "dropped_task_count": 2,
                "terminal_transition_count": 3,
                "reward_bearing_transition_count": 3,
                "pending_at_horizon_count": None,
                "trace_bank_disjoint": True,
                "trace_bank_ids": {"training": "train-bank", "evaluation": "eval-bank"},
                "trace_ids": [f"eval-{index:03d}" for index in range(100)],
                "evaluation_on_training_traces": False,
            },
            "completed_task_count": 1,
            "dropped_task_count": 2,
            "pending_at_horizon_count": 0,
            "comparison_ready": True,
            "claim_safety_status": {
                "paper_reproduction_claim_made": False,
                "performance_superiority_claim_made": False,
                "baseline_superiority_claim_made": False,
                "claim_safety_passed": True,
            },
        }
        for index, budget in enumerate(budgets)
    ]


def _base_report_kwargs() -> dict[str, object]:
    return {
        "feature_id": "063-staged-training-budget-learning-curve",
        "prerequisite_tags_verified": [
            {"name": "branch", "verified": True, "details": "branch"},
            {"name": "feature_062_report_valid", "verified": True, "details": "062"},
            {"name": "baseline_reference_available", "verified": True, "details": "060"},
        ],
        "feature_062_prerequisite_verified": True,
        "training_mode": "cumulative_staged",
        "checkpoint_budgets": [100, 150, 200, 500],
        "evaluation_episode_count_per_checkpoint": 100,
        "episode_length": 110,
        "training_rerun_from_scratch": False,
        "total_max_training_budget": 500,
        "baseline_reference_summary": {
            "available": True,
            "artifact_path": "artifacts/analysis/full-paper-default-training-campaign-execution/baseline-evaluation-metrics.json",
            "baseline_policy_names": ["local-only", "random-legal", "fixed-horizontal"],
            "evaluated_policy_count": 3,
            "actual_baseline_evaluation_episode_count": 100,
            "baseline_metrics_real_execution": True,
            "no_baseline_superiority_claim": True,
            "baseline_policy_episode_counts": {"local-only": 100, "random-legal": 100, "fixed-horizontal": 100},
        },
        "checkpoint_metrics": _base_checkpoint_metrics(),
        "comparison_readiness_summary": {
            "comparison_ready": True,
            "checkpoint_budgets": [100, 150, 200, 500],
            "ready_checkpoint_budgets": [100, 150, 200, 500],
            "unready_checkpoint_budgets": [],
            "evaluation_episode_count_per_checkpoint": 100,
            "episode_length": 110,
            "training_mode": "cumulative_staged",
            "baseline_reference_reused": True,
            "baseline_reference_artifact_path": "artifacts/analysis/full-paper-default-training-campaign-execution/baseline-evaluation-metrics.json",
            "baseline_reference_summary": {"available": True},
            "no_paper_reproduction_claim": True,
            "no_performance_superiority_claim": True,
            "no_baseline_superiority_claim": True,
            "descriptive_only": True,
        },
        "staged_comparative_table_summary": {
            "rows": [
                {
                    "training_budget": 100,
                    "cumulative_training_episode_count": 100,
                    "evaluation_mean_reward": -0.1,
                    "optimizer_step_count": 10,
                    "replay_size": 100,
                    "loss_count": 3,
                    "last_loss": 0.25,
                    "action_count_total": 100,
                    "action_accounting_reconciled": True,
                    "comparison_ready": True,
                    "claim_safety_passed": True,
                }
            ],
            "comparison_ready": True,
            "comparison_scope": "comparison readiness and descriptive trend analysis only",
            "baseline_reference_reused": True,
        },
        "figure_manifest": {
            "figure_directory": "artifacts/analysis/staged-training-budget-learning-curve/figures",
            "figure_files": [
                "figure_01_eval_reward_by_training_budget.png",
                "figure_02_replay_size_and_optimizer_steps_by_budget.png",
                "figure_03_action_distribution_by_training_budget.png",
                "figure_04_loss_by_training_budget.png",
                "figure_05_comparison_readiness_by_budget.png",
            ],
            "figure_count": 5,
            "figures_generated": True,
        },
        "claim_safety_status": {
            "paper_reproduction_claim_made": False,
            "performance_superiority_claim_made": False,
            "baseline_superiority_claim_made": False,
            "claim_safety_passed": True,
        },
        "remaining_blockers": [],
        "recommended_next_feature": "Feature 064 — Final Review and Release Gate Batch",
        "final_verdict": "staged_training_budget_learning_curve_ready",
    }


class StagedTrainingBudgetLearningCurveSchemaTests(unittest.TestCase):
    def test_report_round_trip_schema(self) -> None:
        report = StagedTrainingBudgetLearningCurveReport(**_base_report_kwargs())
        payload = report.to_dict()
        self.assertEqual(payload["feature_id"], "063-staged-training-budget-learning-curve")
        self.assertEqual(payload["final_verdict"], "staged_training_budget_learning_curve_ready")
        self.assertEqual(payload["checkpoint_budgets"], [100, 150, 200, 500])
        self.assertTrue(payload["comparison_readiness_summary"]["comparison_ready"])

    def test_report_rejects_non_cumulative_budget_list(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["checkpoint_budgets"] = [100, 150, 250, 500]
        with self.assertRaises(ValueError):
            StagedTrainingBudgetLearningCurveReport(**kwargs)

    def test_report_rejects_ready_verdict_with_blockers(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["remaining_blockers"] = ["trainer_staging_blocked"]
        with self.assertRaises(ValueError):
            StagedTrainingBudgetLearningCurveReport(**kwargs)

    def test_report_rejects_unsupported_claims(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["claim_safety_status"]["paper_reproduction_claim_made"] = True
        with self.assertRaises(ValueError):
            StagedTrainingBudgetLearningCurveReport(**kwargs)


if __name__ == "__main__":
    unittest.main()
