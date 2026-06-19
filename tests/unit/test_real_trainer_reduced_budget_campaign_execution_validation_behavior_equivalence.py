from __future__ import annotations

import unittest

from src.analysis.real_trainer_reduced_budget_campaign_execution_validation import build_real_trainer_reduced_budget_campaign_execution_validation_report


class RealTrainerReducedBudgetCampaignExecutionValidationBehaviorEquivalenceTests(unittest.TestCase):
    def test_safety_summary_covers_no_claim_and_no_drift_guards(self) -> None:
        payload = build_real_trainer_reduced_budget_campaign_execution_validation_report().to_dict()
        for key in (
            "no_full_campaign_execution",
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

    def test_prerequisite_tag_names_are_unique(self) -> None:
        payload = build_real_trainer_reduced_budget_campaign_execution_validation_report().to_dict()
        names = [entry["name"] for entry in payload["prerequisite_tags_verified"]]
        self.assertEqual(len(names), len(set(names)))


if __name__ == "__main__":
    unittest.main()
