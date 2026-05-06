from __future__ import annotations

import unittest

from src.evaluation.policy_registry import PolicyRegistry
from src.policies import (
    AdaptiveOffloadingPolicy,
    BalancedCooperationOffloadingPolicy,
    FullLocalComputingPolicy,
    HorizontalOffloadingPolicy,
    MinimumLatencyEstimateOffloadingPolicy,
    RandomOffloadingPolicy,
    VerticalOffloadingPolicy,
)


class PolicyRegistryTests(unittest.TestCase):
    def test_all_policies_are_registered(self) -> None:
        self.assertEqual(
            PolicyRegistry.supported_names(),
            ("FLC", "VO", "HO", "RO", "BCO", "MLEO", "ADAPTIVE"),
        )
        self.assertIsInstance(PolicyRegistry.resolve("FLC"), FullLocalComputingPolicy)
        self.assertIsInstance(PolicyRegistry.resolve("VO"), VerticalOffloadingPolicy)
        self.assertIsInstance(PolicyRegistry.resolve("HO"), HorizontalOffloadingPolicy)
        self.assertIsInstance(PolicyRegistry.resolve("RO"), RandomOffloadingPolicy)
        self.assertIsInstance(PolicyRegistry.resolve("BCO"), BalancedCooperationOffloadingPolicy)
        self.assertIsInstance(PolicyRegistry.resolve("MLEO"), MinimumLatencyEstimateOffloadingPolicy)
        self.assertIsInstance(PolicyRegistry.resolve("ADAPTIVE"), AdaptiveOffloadingPolicy)

    def test_unsupported_policy_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            PolicyRegistry.resolve("UNKNOWN")


if __name__ == "__main__":
    unittest.main()
