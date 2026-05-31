from __future__ import annotations

import unittest

from src.evaluation.policy_registry import PolicyRegistry
from src.policies import (
    BalancedCooperationOffloadingPolicy,
    FullLocalComputingPolicy,
    HorizontalOffloadingPolicy,
    MinimumLatencyEstimateOffloadingPolicy,
    RandomOffloadingPolicy,
    VerticalOffloadingPolicy,
)


class BaselinePolicyComparativeEvaluationReadinessRegistryTests(unittest.TestCase):
    def test_required_policies_exist_in_the_registry(self) -> None:
        expected_types = {
            "FLC": FullLocalComputingPolicy,
            "VO": VerticalOffloadingPolicy,
            "HO": HorizontalOffloadingPolicy,
            "RO": RandomOffloadingPolicy,
            "BCO": BalancedCooperationOffloadingPolicy,
            "MLEO": MinimumLatencyEstimateOffloadingPolicy,
        }
        for policy_id, expected_type in expected_types.items():
            with self.subTest(policy_id=policy_id):
                policy = PolicyRegistry.resolve(policy_id)
                self.assertIsInstance(policy, expected_type)

    def test_lower_case_aliases_are_not_required_for_the_comparative_contract(self) -> None:
        self.assertEqual(
            PolicyRegistry.supported_names(),
            ("FLC", "VO", "HO", "RO", "BCO", "MLEO", "ADAPTIVE"),
        )


if __name__ == "__main__":
    unittest.main()
