from __future__ import annotations

import unittest

from src.analysis.real_trainer_reduced_budget_campaign_execution_validation import build_real_trainer_reduced_budget_campaign_execution_validation_report


class RealTrainerReducedBudgetCampaignExecutionValidationIntegrationTests(unittest.TestCase):
    def test_generated_report_passes(self) -> None:
        payload = build_real_trainer_reduced_budget_campaign_execution_validation_report().to_dict()
        self.assertEqual(payload["final_verdict"], "real_trainer_reduced_budget_campaign_validation_passed")
        self.assertEqual(payload["remaining_blockers"], [])
        self.assertEqual(payload["recommended_next_feature"], "Feature 060 — Full Paper-Default Training Campaign Execution")
        self.assertTrue(payload["feature_059_gate_verified"])
        self.assertTrue(payload["feature_058_harness_verified"])
        self.assertTrue(payload["feature_057_pilot_verified"])


if __name__ == "__main__":
    unittest.main()
