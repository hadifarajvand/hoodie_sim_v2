from __future__ import annotations

import unittest

from src.evaluation.policy_registry import PolicyRegistry
from src.policies import (
    AdaptiveOffloadingPolicy,
    BalancedCooperationOffloadingPolicy,
    FullLocalComputingPolicy,
    HorizontalOffloadingPolicy,
    MinimumLatencyEstimateOffloadingPolicy,
    PolicyContext,
    RandomOffloadingPolicy,
    VerticalOffloadingPolicy,
)


class PolicyRegistryTests(unittest.TestCase):
    def test_required_paper_baselines_are_registered_and_choose_through_context(self) -> None:
        expected_types = {
            "FLC": FullLocalComputingPolicy,
            "VO": VerticalOffloadingPolicy,
            "HO": HorizontalOffloadingPolicy,
            "RO": RandomOffloadingPolicy,
            "BCO": BalancedCooperationOffloadingPolicy,
            "MLEO": MinimumLatencyEstimateOffloadingPolicy,
        }
        self.assertEqual(
            PolicyRegistry.supported_names(),
            ("FLC", "VO", "HO", "RO", "BCO", "MLEO", "ADAPTIVE"),
        )
        context = PolicyContext(
            observation={
                "fallback_hints": {"local": 1.0},
                "mleo_delay_candidates": {
                    "local": {"queue_delay": 1.0, "transmission_delay": 0.0, "compute_delay": 1.0}
                },
            },
            legal_action_mask={"local": True, "horizontal": False, "vertical": False},
        )
        for name, expected_type in expected_types.items():
            with self.subTest(name=name):
                policy = PolicyRegistry.resolve(name)
                self.assertIsInstance(policy, expected_type)
                self.assertEqual(policy.choose_action(context), "local")

    def test_existing_adaptive_alias_is_registered(self) -> None:
        self.assertIsInstance(PolicyRegistry.resolve("ADAPTIVE"), AdaptiveOffloadingPolicy)
        self.assertIsInstance(PolicyRegistry.resolve("Adaptive"), AdaptiveOffloadingPolicy)

    def test_hoodie_cannot_resolve_to_a_heuristic(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported policy name"):
            PolicyRegistry.resolve("HOODIE")

    def test_paper_baseline_aliases_are_preserved(self) -> None:
        aliases = {
            "full-local-computing": FullLocalComputingPolicy,
            "vertical_offloading": VerticalOffloadingPolicy,
            "horizontal_offloading": HorizontalOffloadingPolicy,
            "random_offloading": RandomOffloadingPolicy,
            "balanced_cooperation_offloading": BalancedCooperationOffloadingPolicy,
            "minimum_latency_estimate_offloading": MinimumLatencyEstimateOffloadingPolicy,
        }
        for alias, expected_type in aliases.items():
            with self.subTest(alias=alias):
                self.assertIsInstance(PolicyRegistry.resolve(alias), expected_type)

    def test_unsupported_policy_is_rejected_with_useful_message(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported policy name.*UNKNOWN.*Supported policies"):
            PolicyRegistry.resolve("UNKNOWN")


if __name__ == "__main__":
    unittest.main()
