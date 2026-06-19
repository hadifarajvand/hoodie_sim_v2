from __future__ import annotations

import unittest
from unittest import mock

from src.analysis.full_paper_default_training_campaign_execution import build_full_paper_default_training_campaign_execution_report
from src.analysis.full_paper_default_training_campaign_execution.model import FullPaperDefaultTrainingCampaignExecutionReport
from tests.unit.test_full_paper_default_training_campaign_execution_schema import _base_report_kwargs


def _mock_execution() -> dict[str, object]:
    return {
        "training_trace_bank_id": "full-training-train-bank",
        "evaluation_trace_bank_id": "full-training-eval-bank",
        "baseline_harness_id": "feature-058-baseline-evaluation-harness",
        "seed_bundle": {"training_trace_generation_seed": 41},
        "replay": [],
        "replay_size": 110000,
        "optimizer_step_count": 2670,
        "target_sync_count": 1,
        "loss_values": [24.95241355895996],
        "loss_is_finite": True,
        "action_distribution": {"local": 33000, "horizontal": 39000, "vertical": 39000},
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
            "baseline_metric_shells": {"local-only": {"reward": {"value": None}}},
            "no_baseline_superiority_claim": True,
        },
        "evaluation_trace_bank_summary": {"evaluation_trace_bank_id": "feature-058-evaluation-trace-bank"},
        "checkpoint_metadata": {
            "stage": "full_training_candidate",
            "feature_id": "041-full-training-reproduction-campaign",
            "seed_bundle": {"training_trace_generation_seed": 41},
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
        "full_result": type("FullResult", (), {"full_campaign_executed": True})(),
    }


class FullPaperDefaultTrainingCampaignExecutionIntegrationTests(unittest.TestCase):
    def test_generated_report_reaches_passed_verdict(self) -> None:
        with mock.patch("src.analysis.full_paper_default_training_campaign_execution.runner._status_paths", return_value=[]), \
            mock.patch("src.analysis.full_paper_default_training_campaign_execution.runner._staged_paths", return_value=[]), \
            mock.patch("src.analysis.full_paper_default_training_campaign_execution.runner._diff_names", return_value=[]), \
            mock.patch("src.analysis.full_paper_default_training_campaign_execution.runner._run_controlled_campaign", return_value=_mock_execution()):
            payload = build_full_paper_default_training_campaign_execution_report().to_dict()
        self.assertTrue(payload["feature_059_gate_verified"])
        self.assertTrue(payload["feature_060a_validation_verified"])
        self.assertTrue(payload["feature_058_harness_verified"])
        self.assertEqual(payload["remaining_blockers"], [])
        self.assertEqual(payload["final_verdict"], "full_paper_default_training_campaign_execution_passed")
        self.assertEqual(payload["recommended_next_feature"], "Feature 061 — Campaign Result Integrity and Comparison Readiness Audit")

    def test_feature_059_gate_blocks_bad_report(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["feature_059_gate_verified"] = False
        kwargs["remaining_blockers"] = ["feature_059_report_valid"]
        kwargs["recommended_next_feature"] = "Repair Feature 059 prerequisite evidence before Feature 060 can proceed"
        kwargs["final_verdict"] = "feature_059_prerequisite_blocked"
        report = FullPaperDefaultTrainingCampaignExecutionReport(**kwargs)
        self.assertEqual(report.final_verdict, "feature_059_prerequisite_blocked")
        self.assertIn("feature_059_report_valid", report.remaining_blockers)


if __name__ == "__main__":
    unittest.main()
