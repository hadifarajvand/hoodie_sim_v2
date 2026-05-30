from __future__ import annotations

import unittest

from src.policies import (
    BalancedCooperationOffloadingPolicy,
    FullLocalComputingPolicy,
    HorizontalOffloadingPolicy,
    PolicyContext,
    RandomOffloadingPolicy,
    VerticalOffloadingPolicy,
)


class BaselinePolicyFidelityTests(unittest.TestCase):
    def test_flc_prefers_concrete_local_action_when_available(self) -> None:
        context = PolicyContext(
            observation={"local_action": "local_7"},
            legal_action_mask={"local_7": True, "local": True, "horizontal": False, "vertical": False},
        )
        self.assertEqual(FullLocalComputingPolicy().choose_action(context), "local_7")

    def test_vo_prefers_concrete_cloud_action_when_available(self) -> None:
        context = PolicyContext(
            observation={"cloud_action": "cloud_21"},
            legal_action_mask={"cloud_21": True, "vertical": True, "horizontal": False, "local": False},
        )
        self.assertEqual(VerticalOffloadingPolicy().choose_action(context), "cloud_21")

    def test_ho_never_selects_source_destination(self) -> None:
        context = PolicyContext(
            observation={"source_agent_id": "1", "horizontal_destinations": ["1", "2", "3"]},
            legal_action_mask={"1": True, "2": True, "3": True, "horizontal": True},
        )
        self.assertIn(HorizontalOffloadingPolicy().choose_action(context), {"2", "3"})

    def test_ro_reproducibly_samples_horizontal_destination_with_seed(self) -> None:
        context = PolicyContext(
            observation={
                "source_agent_id": "1",
                "horizontal_destinations": ["1", "2", "3"],
            },
            legal_action_mask={
                "local": True,
                "horizontal": True,
                "vertical": True,
                "2": True,
                "3": True,
            },
        )
        first = RandomOffloadingPolicy(seed=7).choose_action(context)
        second = RandomOffloadingPolicy(seed=7).choose_action(context)
        self.assertEqual(first, second)
        self.assertNotEqual(first, "1")

    def test_bco_compatibility_fallback_rotates_legacy_families(self) -> None:
        policy = BalancedCooperationOffloadingPolicy()
        context = PolicyContext(
            observation={},
            legal_action_mask={"local": True, "cloud": True, "2": True, "3": True},
        )
        self.assertEqual([policy.choose_action(context) for _ in range(4)], ["local", "cloud", "2", "3"])


if __name__ == "__main__":
    unittest.main()
