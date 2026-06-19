from __future__ import annotations

import unittest

from src.analysis.real_trainer_reduced_budget_campaign_execution_validation import build_real_trainer_reduced_budget_campaign_execution_validation_report


class RealTrainerReducedBudgetCampaignExecutionValidationMetricsTests(unittest.TestCase):
    def test_reduced_budget_report_has_real_trainer_and_growth_evidence(self) -> None:
        payload = build_real_trainer_reduced_budget_campaign_execution_validation_report().to_dict()
        self.assertEqual(payload["final_verdict"], "real_trainer_reduced_budget_campaign_validation_passed")
        self.assertTrue(payload["reduced_budget_execution_summary"]["actual_budget_is_reduced_for_validation"])
        self.assertFalse(payload["reduced_budget_execution_summary"]["full_campaign_executed"])
        self.assertTrue(payload["reduced_budget_execution_summary"]["real_trainer_used"])
        self.assertEqual(payload["real_trainer_binding_summary"]["real_trainer_class"], "src.analysis.full_training_reproduction_campaign.trainer.DDQNTrainer")
        self.assertEqual(payload["real_trainer_binding_summary"]["trainer_method_called"], "DDQNTrainer.run_pilot")
        self.assertGreater(payload["training_metrics_summary"]["optimizer_step_count"], 0)
        self.assertGreater(payload["training_metrics_summary"]["replay_size"], 0)
        self.assertGreater(payload["training_metrics_summary"]["loss_count"], 0)
        self.assertTrue(payload["training_metrics_summary"]["loss_finite"])
        self.assertGreater(payload["evaluation_metrics_summary"]["evaluation_episode_count"], 0)
        self.assertTrue(payload["baseline_contract_summary"]["baseline_harness_ready"])
        self.assertTrue(payload["checkpoint_metadata_summary"]["checkpoint_schema_valid"])


if __name__ == "__main__":
    unittest.main()
