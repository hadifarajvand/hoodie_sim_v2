from __future__ import annotations

import unittest

from src.baselines import FullLocalComputing, HorizontalOffloader, RandomOffloader, VerticalOffloader


class BaselinePolicyLegalityTests(unittest.TestCase):
    def test_policies_select_legal_destinations(self) -> None:
        legal = ["local", "6", "11", "16", "cloud"]
        self.assertIn(RandomOffloader(seed=7).select(legal), legal)
        self.assertEqual(FullLocalComputing().select(legal), "local")
        self.assertEqual(VerticalOffloader().select(legal), "cloud")
        self.assertIn(HorizontalOffloader().select(legal), {"6", "11", "16"})


if __name__ == "__main__":
    unittest.main()

