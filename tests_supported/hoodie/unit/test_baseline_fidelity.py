from __future__ import annotations

import unittest

from src.policies.bco import BalancedCooperationOffloadingPolicy
from src.policies.flc import FullLocalComputingPolicy
from src.policies.ho import HorizontalOffloadingPolicy
from src.policies.mleo import MinimumLatencyEstimateOffloadingPolicy
from src.policies.policy_interface import PolicyContext
from src.policies.ro import RandomOffloadingPolicy
from src.policies.vo import VerticalOffloadingPolicy
from src.policies import build_legal_action_mask


class BaselineFidelityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.context = PolicyContext(
            observation={
                "balance_hint": {"local": 5.0, "horizontal": 2.0, "vertical": 8.0},
                "latency_estimates": {"local": 5.0, "horizontal": 2.0, "vertical": 8.0},
                "mleo_delay_candidates": {
                    "local": {"action_id": "local", "total_delay": 5.0},
                    "horizontal": {"action_id": "horizontal", "total_delay": 2.0},
                    "vertical": {"action_id": "vertical", "total_delay": 8.0},
                },
                "queue_load": 3.0,
                "destination_loads": {"local": 6.0, "horizontal": 1.0, "vertical": 9.0},
            },
            legal_action_mask=build_legal_action_mask(("local", "horizontal", "vertical")),
            trace_history=("immutable", "trace"),
        )

    def test_flc_ro_ho_vo_bco_mleo_source_contracts(self) -> None:
        self.assertEqual(FullLocalComputingPolicy().choose_action(self.context), "local")
        self.assertIn(RandomOffloadingPolicy(seed=1).choose_action(self.context), {"local", "horizontal", "vertical"})
        self.assertEqual(HorizontalOffloadingPolicy().choose_action(self.context), "horizontal")
        self.assertEqual(VerticalOffloadingPolicy().choose_action(self.context), "vertical")
        self.assertEqual(BalancedCooperationOffloadingPolicy().choose_action(self.context), "horizontal")
        self.assertEqual(MinimumLatencyEstimateOffloadingPolicy().choose_action(self.context), "horizontal")

    def test_bco_reacts_to_load_imbalance(self) -> None:
        low = PolicyContext(
            observation={"queue_load": 0.0, "destination_loads": {"local": 9.0, "horizontal": 1.0, "vertical": 8.0}},
            legal_action_mask=build_legal_action_mask(("local", "horizontal", "vertical")),
            trace_history=(),
        )
        high = PolicyContext(
            observation={"queue_load": 0.0, "destination_loads": {"local": 1.0, "horizontal": 9.0, "vertical": 8.0}},
            legal_action_mask=build_legal_action_mask(("local", "horizontal", "vertical")),
            trace_history=(),
        )
        self.assertEqual(BalancedCooperationOffloadingPolicy().choose_action(low), "horizontal")
        self.assertEqual(BalancedCooperationOffloadingPolicy().choose_action(high), "local")

    def test_every_policy_respects_legal_mask(self) -> None:
        mask = build_legal_action_mask(("local", "vertical"))
        context = PolicyContext(observation={"latency_estimates": {"local": 1.0, "vertical": 0.5}}, legal_action_mask=mask, trace_history=())
        policies = [
            FullLocalComputingPolicy(),
            RandomOffloadingPolicy(seed=2),
            HorizontalOffloadingPolicy(),
            VerticalOffloadingPolicy(),
            BalancedCooperationOffloadingPolicy(),
            MinimumLatencyEstimateOffloadingPolicy(),
        ]
        for policy in policies:
            self.assertIn(policy.choose_action(context), {"local", "vertical"})


if __name__ == "__main__":
    unittest.main()
