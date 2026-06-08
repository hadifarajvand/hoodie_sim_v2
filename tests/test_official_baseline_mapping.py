from __future__ import annotations

import unittest

from decision_makers import AllHorizontal, AllLocal, AllVertical, Random
from decision_makers.baselines import BalancedCyclicOffloader, MinimumLatencyEstimationOffloader, official_policy_map


class OfficialBaselineMappingTests(unittest.TestCase):
    def test_active_policy_set_is_exact(self) -> None:
        self.assertEqual(
            sorted(official_policy_map().keys()),
            ["BCO", "FLC", "HO", "HOODIE", "MLEO", "RO", "VO"],
        )

    def test_random_alias_is_random(self) -> None:
        self.assertIs(official_policy_map()["RO"], "random")
        self.assertIsInstance(Random(5), Random)

    def test_flc_alias_is_all_local(self) -> None:
        self.assertIs(official_policy_map()["FLC"], "all_local")
        self.assertIsInstance(AllLocal(), AllLocal)

    def test_vo_alias_is_all_vertical(self) -> None:
        self.assertIs(official_policy_map()["VO"], "all_vertical")
        self.assertIsInstance(AllVertical(5), AllVertical)

    def test_ho_alias_is_all_horizontal(self) -> None:
        self.assertIs(official_policy_map()["HO"], "all_horizontal")
        self.assertIsInstance(AllHorizontal(5), AllHorizontal)

    def test_bco_alias_is_balanced_cyclic(self) -> None:
        self.assertIs(official_policy_map()["BCO"], "balanced_cyclic")
        policy = BalancedCyclicOffloader(6)
        actions = [policy.choose_action() for _ in range(4)]
        self.assertEqual(actions, [0, 5, 1, 2])

    def test_mleo_raises_loudly(self) -> None:
        self.assertIs(official_policy_map()["MLEO"], "mleo")
        with self.assertRaisesRegex(
            NotImplementedError,
            "MLEO is not implemented as paper-faithful candidate-wise minimum latency estimation",
        ):
            MinimumLatencyEstimationOffloader()


if __name__ == "__main__":
    unittest.main()
