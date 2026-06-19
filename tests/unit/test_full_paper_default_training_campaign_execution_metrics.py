from __future__ import annotations

import unittest
from unittest import mock

from src.analysis.full_paper_default_training_campaign_execution import build_full_paper_default_training_campaign_execution_report
from src.analysis.full_paper_default_training_campaign_execution.model import FullPaperDefaultTrainingCampaignExecutionReport
from tests.unit.test_full_paper_default_training_campaign_execution_schema import _base_report_kwargs, _baseline_metrics


def _mock_execution() -> dict[str, object]:
    return {
        "campaign_config": object(),
        "training_trace_bank_id": "full-training-train-bank",
        "evaluation_trace_bank_id": "full-training-eval-bank",
        "baseline_harness_id": "feature-058-baseline-evaluation-harness",
        "seed_bundle": {
            "training_trace_generation_seed": 41,
            "evaluation_trace_generation_seed": 43,
            "baseline_policy_seed": 6101,
        },
        "replay": [],
        "replay_size": 110000,
        "optimizer_step_count": 2670,
        "target_sync_count": 1,
        "loss_values": [24.95241355895996],
        "loss_is_finite": True,
        "action_distribution": {"local": 33000, "horizontal": 38000, "vertical": 39000, "invalid_or_noop_action_count": 0},
        "reward_summary": {"reward_count": 1000, "reward_available_count": 1000, "total_reward": -2000.0, "mean_reward": -2.0, "pending_at_horizon_count": 0},
        "evaluation": {
            "evaluation_episode_count": 100,
            "mean_reward": -40.0,
            "completed_task_count": 0,
            "dropped_task_count": 0,
            "terminal_transition_count": 0,
            "reward_bearing_transition_count": 0,
            "trace_bank_disjoint": True,
            "trace_bank_ids": {"training": "full-training-train-bank", "evaluation": "full-training-eval-bank"},
            "trace_ids": [f"eval-{index:03d}" for index in range(100)],
            "evaluation_on_training_traces": False,
            "candidate_reproduction_supported": False,
        },
        "baseline_evaluation_summary": {
            "baseline_policy_names": ["local-only", "random-legal", "fixed-horizontal"],
            "evaluated_policy_count": 3,
            "actual_baseline_evaluation_episode_count": 100,
            "per_policy_metrics": _baseline_metrics(),
            "baseline_metric_shells": _baseline_metrics(),
            "baseline_metrics_real_execution": True,
            "no_baseline_superiority_claim": True,
        },
        "evaluation_trace_bank_summary": {
            "evaluation_trace_bank_id": "feature-058-evaluation-trace-bank",
        },
        "checkpoint_metadata": {
            "stage": "full_training_candidate",
            "feature_id": "041-full-training-reproduction-campaign",
            "seed_bundle": {
                "training_trace_generation_seed": 41,
                "evaluation_trace_generation_seed": 43,
                "baseline_policy_seed": 6101,
            },
            "target_update_unit": "optimizer_step",
            "config_hash": "abc123",
            "train_trace_bank_id": "full-training-train-bank",
            "eval_trace_bank_id": "full-training-eval-bank",
            "optimizer_step_count": 2670,
            "replay_size": 110000,
            "full_campaign_enabled": True,
        },
        "binding_evidence": {
            "torch_import_used": True,
            "real_trainer_import_used": True,
            "real_trainer_class": "src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer",
            "real_trainer_instantiated": True,
            "real_trainer_method_called": "DDQNTrainer.run_full_candidate",
            "full_campaign_executed": True,
            "full_campaign_block_reason": None,
        },
        "full_result": mock.Mock(full_campaign_executed=True),
    }


class FullPaperDefaultTrainingCampaignExecutionMetricsTests(unittest.TestCase):
    def test_generated_report_has_training_evaluation_and_baseline_metrics(self) -> None:
        with mock.patch("src.analysis.full_paper_default_training_campaign_execution.runner._status_paths", return_value=[]), \
            mock.patch("src.analysis.full_paper_default_training_campaign_execution.runner._staged_paths", return_value=[]), \
            mock.patch("src.analysis.full_paper_default_training_campaign_execution.runner._diff_names", return_value=[]), \
            mock.patch("src.analysis.full_paper_default_training_campaign_execution.runner._run_controlled_campaign", return_value=_mock_execution()):
            payload = build_full_paper_default_training_campaign_execution_report().to_dict()

        self.assertEqual(payload["final_verdict"], "full_paper_default_training_campaign_execution_passed")
        self.assertEqual(payload["recommended_next_feature"], "Feature 061 — Campaign Result Integrity and Comparison Readiness Audit")
        self.assertEqual(payload["training_metrics_summary"]["optimizer_step_count"], 2670)
        self.assertEqual(payload["training_metrics_summary"]["replay_size"], 110000)
        self.assertEqual(sum(payload["training_metrics_summary"]["action_distribution"].values()), 110000)
        self.assertTrue(payload["training_metrics_summary"]["action_accounting_reconciled"])
        self.assertEqual(payload["training_metrics_summary"]["loss_count"], 1)
        self.assertTrue(payload["training_metrics_summary"]["loss_finite"])
        self.assertEqual(payload["evaluation_metrics_summary"]["evaluation_episode_count"], 100)
        self.assertTrue(payload["evaluation_metrics_summary"]["metric_schema_coverage"]["metric_schema_complete"])
        self.assertEqual(payload["baseline_evaluation_summary"]["evaluated_policy_count"], 3)
        self.assertTrue(payload["baseline_evaluation_summary"]["baseline_metrics_real_execution"])
        for metrics in payload["baseline_evaluation_summary"]["per_policy_metrics"].values():
            self.assertEqual(metrics["episode_count"], 100)
            self.assertFalse(metrics["metric_shell_only"])
            self.assertFalse(metrics["performance_claim"])
            self.assertTrue(metrics["no_baseline_superiority_claim"])
        self.assertEqual(payload["campaign_execution_summary"]["actual_training_episode_count"], 1000)
        self.assertEqual(payload["campaign_execution_summary"]["actual_evaluation_episode_count"], 100)
        self.assertEqual(payload["campaign_execution_summary"]["actual_baseline_evaluation_episode_count"], 100)

    def test_artifact_manifest_must_be_complete(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["artifact_manifest_summary"]["all_required_artifacts_exist"] = False
        with self.assertRaises(ValueError):
            FullPaperDefaultTrainingCampaignExecutionReport(**kwargs)

    def test_training_metrics_missing_optimizer_steps_cannot_pass(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["training_metrics_summary"]["optimizer_step_count"] = 0
        with self.assertRaises(ValueError):
            FullPaperDefaultTrainingCampaignExecutionReport(**kwargs)


if __name__ == "__main__":
    unittest.main()
