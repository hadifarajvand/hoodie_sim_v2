from __future__ import annotations

import unittest

from src.policies import (
    BalancedCooperationOffloadingPolicy,
    FullLocalComputingPolicy,
    HorizontalOffloadingPolicy,
    MinimumLatencyEstimateOffloadingPolicy,
    PolicyContext,
    RandomOffloadingPolicy,
    VerticalOffloadingPolicy,
    build_legal_action_mask,
)


class PolicyInterfaceRegressionTests(unittest.TestCase):
    def test_existing_baselines_still_choose_through_policy_context(self) -> None:
        context = PolicyContext(
            observation={
                "balance_hint": {"local": 1.0, "horizontal": 2.0, "vertical": 3.0},
                "latency_estimates": {"local": 3.0, "horizontal": 1.0, "vertical": 2.0},
            },
            legal_action_mask=build_legal_action_mask(("local", "horizontal", "vertical")),
        )

        self.assertEqual(FullLocalComputingPolicy().choose_action(context), "local")
        self.assertEqual(HorizontalOffloadingPolicy().choose_action(context), "horizontal")
        self.assertEqual(VerticalOffloadingPolicy().choose_action(context), "vertical")
        self.assertEqual(BalancedCooperationOffloadingPolicy().choose_action(context), "local")
        self.assertEqual(MinimumLatencyEstimateOffloadingPolicy().choose_action(context), "horizontal")
        self.assertIn(RandomOffloadingPolicy(seed=1).choose_action(context), {"local", "horizontal", "vertical"})


if __name__ == "__main__":
    unittest.main()
