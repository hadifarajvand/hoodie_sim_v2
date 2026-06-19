from __future__ import annotations

import unittest

from src.analysis.full_paper_default_training_campaign_execution import build_full_paper_default_training_campaign_execution_report
from src.analysis.full_paper_default_training_campaign_execution.model import FullPaperDefaultTrainingCampaignExecutionReport
from tests.unit.test_full_paper_default_training_campaign_execution_schema import _base_report_kwargs


class FullPaperDefaultTrainingCampaignExecutionMetricsTests(unittest.TestCase):
    def test_generated_report_has_training_evaluation_and_baseline_metrics(self) -> None:
        payload = build_full_paper_default_training_campaign_execution_report().to_dict()
        self.assertEqual(payload["final_verdict"], "full_paper_default_training_campaign_execution_passed")
        self.assertEqual(payload["recommended_next_feature"], "Feature 061 — Campaign Result Integrity and Comparison Readiness Audit")
        self.assertGreater(payload["training_metrics_summary"]["optimizer_step_count"], 0)
        self.assertGreater(payload["training_metrics_summary"]["replay_size"], 0)
        self.assertGreater(payload["training_metrics_summary"]["loss_count"], 0)
        self.assertTrue(payload["training_metrics_summary"]["loss_finite"])
        self.assertGreater(payload["evaluation_metrics_summary"]["evaluation_episode_count"], 0)
        self.assertTrue(payload["evaluation_metrics_summary"]["metric_schema_coverage"]["metric_schema_complete"])
        self.assertGreater(payload["baseline_evaluation_summary"]["evaluated_policy_count"], 0)

    def test_counts_are_actual_reduced_budget_not_configured_budget_fabrication(self) -> None:
        payload = build_full_paper_default_training_campaign_execution_report().to_dict()
        configured = payload["campaign_execution_summary"]["configured_budget"]
        actual = payload["campaign_execution_summary"]["actual_training_episode_count"]
        self.assertEqual(actual, 1)
        self.assertEqual(payload["resource_control_summary"]["actual_executed_budget"], {"training_episode_count": 1, "evaluation_episode_count": 3, "baseline_evaluation_episode_count": 1})
        self.assertEqual(configured, {"training_episode_count": 1000, "evaluation_episode_count": 100, "baseline_evaluation_episode_count": 100})
        self.assertTrue(payload["campaign_execution_summary"]["execution_completed"])

    def test_training_metrics_missing_optimizer_steps_cannot_pass(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["training_metrics_summary"]["optimizer_step_count"] = 0
        with self.assertRaises(ValueError):
            FullPaperDefaultTrainingCampaignExecutionReport(**kwargs)

    def test_required_artifact_manifest_must_be_complete(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["artifact_manifest_summary"]["all_required_artifacts_exist"] = False
        with self.assertRaises(ValueError):
            FullPaperDefaultTrainingCampaignExecutionReport(**kwargs)


if __name__ == "__main__":
    unittest.main()
