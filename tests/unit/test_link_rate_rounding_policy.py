from __future__ import annotations

import unittest

from src.environment.link_rate_config import seconds_to_slots, slots_to_seconds


class LinkRateRoundingPolicyTests(unittest.TestCase):
    def test_ceil_rounding_is_deterministic(self) -> None:
        self.assertEqual(seconds_to_slots(0.0, 0.25), 0)
        self.assertEqual(seconds_to_slots(0.24, 0.25), 1)
        self.assertEqual(seconds_to_slots(0.5, 0.25), 2)

    def test_exact_rounding_rejects_fractional_slots(self) -> None:
        with self.assertRaises(ValueError):
            seconds_to_slots(0.3, 0.25, rounding_policy="exact")
        self.assertEqual(seconds_to_slots(0.5, 0.25, rounding_policy="exact"), 2)

    def test_slots_to_seconds_is_the_inverse_conversion(self) -> None:
        self.assertEqual(slots_to_seconds(3, 0.25), 0.75)


if __name__ == "__main__":
    unittest.main()
