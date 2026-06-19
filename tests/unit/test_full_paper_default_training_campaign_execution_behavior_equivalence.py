from __future__ import annotations

import unittest
from unittest import mock

from src.analysis.full_paper_default_training_campaign_execution import build_full_paper_default_training_campaign_execution_report
from src.analysis.full_paper_default_training_campaign_execution.config import FullPaperDefaultTrainingCampaignExecutionConfig
from src.analysis.full_paper_default_training_campaign_execution.model import FullPaperDefaultTrainingCampaignExecutionReport
from tests.unit.test_full_paper_default_training_campaign_execution_schema import _base_report_kwargs, _baseline_metrics


class FullPaperDefaultTrainingCampaignExecutionBehaviorEquivalenceTests(unittest.TestCase):
    def test_behavior_equivalence_check_names_are_unique(self) -> None:
        kwargs = _base_report_kwargs()
        report = FullPaperDefaultTrainingCampaignExecutionReport(**kwargs)
        names = [entry["name"] for entry in report.to_dict()["prerequisite_tags_verified"]]
        self.assertEqual(len(names), len(set(names)))

    def test_safety_fields_cover_no_claim_and_no_drift_guards(self) -> None:
        kwargs = _base_report_kwargs()
        report = FullPaperDefaultTrainingCampaignExecutionReport(**kwargs)
        payload = report.to_dict()
        for key in (
            "no_paper_reproduction_claim",
            "no_performance_superiority_claim",
            "no_baseline_superiority_claim",
            "no_uncontrolled_campaign_loop",
            "no_policy_drift",
            "no_dependency_drift",
            "no_environment_contract_drift",
            "no_reward_timing_change",
            "no_prior_artifact_rewrite",
        ):
            self.assertIn(key, payload["safety_summary"])
            self.assertTrue(payload["safety_summary"][key])

    def test_forbidden_claim_flags_are_rejected_by_config(self) -> None:
        for kwargs in (
            {"paper_reproduction_claim": True},
            {"performance_superiority_claim": True},
            {"baseline_superiority_claim": True},
            {"uncontrolled_campaign_loop": True},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    FullPaperDefaultTrainingCampaignExecutionConfig(**kwargs)

    def test_safety_false_cannot_claim_pass(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["safety_summary"]["no_paper_reproduction_claim"] = False
        with self.assertRaises(ValueError):
            FullPaperDefaultTrainingCampaignExecutionReport(**kwargs)

    def test_report_builder_keeps_training_drift_free_when_stubbed(self) -> None:
        execution = {
            "training_trace_bank_id": "full-training-train-bank",
            "evaluation_trace_bank_id": "full-training-eval-bank",
            "baseline_harness_id": "feature-058-baseline-evaluation-harness",
            "seed_bundle": {"training_trace_generation_seed": 41},
            "replay": [],
            "replay_size": 110000,
            "optimizer_step_count": 2670,
            "target_sync_count": 1,
            "loss_values": [1.0],
            "loss_is_finite": True,
            "action_distribution": {"local": 109998, "horizontal": 1, "vertical": 1, "invalid_or_noop_action_count": 0},
            "reward_summary": {"reward_count": 1},
            "evaluation": {
                "evaluation_episode_count": 100,
                "mean_reward": -40.0,
                "completed_task_count": 0,
                "dropped_task_count": 0,
                "terminal_transition_count": 0,
                "reward_bearing_transition_count": 0,
                "trace_bank_disjoint": True,
                "trace_bank_ids": {"training": "full-training-train-bank", "evaluation": "full-training-eval-bank"},
                "trace_ids": ["eval-000"],
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
        with mock.patch("src.analysis.full_paper_default_training_campaign_execution.runner._status_paths", return_value=[]), \
            mock.patch("src.analysis.full_paper_default_training_campaign_execution.runner._staged_paths", return_value=[]), \
            mock.patch("src.analysis.full_paper_default_training_campaign_execution.runner._diff_names", return_value=[]), \
            mock.patch("src.analysis.full_paper_default_training_campaign_execution.runner._run_controlled_campaign", return_value=execution):
            payload = build_full_paper_default_training_campaign_execution_report().to_dict()
        self.assertTrue(payload["safety_summary"]["no_policy_drift"])
        self.assertTrue(payload["safety_summary"]["no_dependency_drift"])
        self.assertTrue(payload["safety_summary"]["no_environment_contract_drift"])


if __name__ == "__main__":
    unittest.main()
