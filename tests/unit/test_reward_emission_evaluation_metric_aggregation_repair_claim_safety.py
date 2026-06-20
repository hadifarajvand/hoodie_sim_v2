from __future__ import annotations

import unittest

from src.analysis.reward_emission_evaluation_metric_aggregation_repair.model import ClaimSafetyStatus, RewardEmissionAggregationRepairReport

from tests.unit.test_reward_emission_evaluation_metric_aggregation_repair_schema import _base_report_kwargs


class RewardEmissionEvaluationMetricAggregationRepairClaimSafetyTests(unittest.TestCase):
    def test_claim_safety_pass_rejects_unsupported_claims(self) -> None:
        with self.assertRaises(ValueError):
            ClaimSafetyStatus(
                paper_reproduction_claim_made=True,
                performance_superiority_claim_made=False,
                baseline_superiority_claim_made=False,
                claim_safety_passed=True,
            )

    def test_ready_report_rejects_blockers_and_failed_claim_safety(self) -> None:
        kwargs = _base_report_kwargs()
        kwargs["remaining_blockers"] = ["reward_reconciliation_failed"]
        kwargs["claim_safety_status"] = {
            "paper_reproduction_claim_made": False,
            "performance_superiority_claim_made": False,
            "baseline_superiority_claim_made": False,
            "claim_safety_passed": False,
        }
        kwargs["final_verdict"] = "reward_emission_aggregation_repair_ready"
        with self.assertRaises(ValueError):
            RewardEmissionAggregationRepairReport(**kwargs)


if __name__ == "__main__":
    unittest.main()
