from __future__ import annotations

import unittest

from src.analysis.campaign_integrity_evaluation_comparison_batch import build_campaign_integrity_evaluation_comparison_batch_report


class CampaignIntegrityEvaluationComparisonBatchMetricsTests(unittest.TestCase):
    def test_baseline_and_trained_results_use_shared_schema_fields(self) -> None:
        payload = build_campaign_integrity_evaluation_comparison_batch_report().to_dict()
        baseline = payload["baseline_evaluation_summary"]
        trained = payload["trained_policy_evaluation_summary"]
        self.assertEqual(baseline["evaluation_trace_bank_id"], "feature-058-evaluation-trace-bank")
        self.assertEqual(trained["evaluation_trace_bank_id"], "feature-058-evaluation-trace-bank")
        self.assertTrue(baseline["controlled_experiment_data"])
        self.assertTrue(trained["controlled_experiment_data"])

    def test_comparison_report_contains_required_metrics(self) -> None:
        payload = build_campaign_integrity_evaluation_comparison_batch_report().to_dict()["comparison_report_summary"]
        for key in (
            "delay",
            "drop",
            "timeout",
            "reward",
            "action_distribution",
            "local_action_count",
            "horizontal_action_count",
            "vertical_action_count",
            "per_episode_summary",
            "train_eval_separation",
            "baseline_policy_metrics",
            "trained_policy_metrics",
        ):
            self.assertIn(key, payload)


if __name__ == "__main__":
    unittest.main()
