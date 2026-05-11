from __future__ import annotations

import unittest

from src.environment.link_rate_config import (
    BITS_PER_MBIT,
    BPS_PER_MBPS,
    bits_to_mbits,
    bps_to_mbps,
    mbits_to_bits,
    mbps_to_bps,
    seconds_to_slots,
    slots_to_seconds,
)


class LinkRateConversionTests(unittest.TestCase):
    def test_bits_and_mbits_conversion_is_exact(self) -> None:
        self.assertEqual(mbits_to_bits(1.0), BITS_PER_MBIT)
        self.assertEqual(bits_to_mbits(BITS_PER_MBIT), 1.0)
        self.assertEqual(mbits_to_bits(bits_to_mbits(2_500_000.0)), 2_500_000.0)

    def test_bps_and_mbps_conversion_is_exact(self) -> None:
        self.assertEqual(mbps_to_bps(1.0), BPS_PER_MBPS)
        self.assertEqual(bps_to_mbps(BPS_PER_MBPS), 1.0)
        self.assertEqual(mbps_to_bps(bps_to_mbps(4_500_000.0)), 4_500_000.0)

    def test_seconds_and_slots_conversion_is_explicit(self) -> None:
        self.assertEqual(seconds_to_slots(0.0, 0.25), 0)
        self.assertEqual(seconds_to_slots(0.25, 0.25), 1)
        self.assertEqual(seconds_to_slots(0.26, 0.25), 2)
        self.assertEqual(slots_to_seconds(4, 0.25), 1.0)

    def test_round_trip_seconds_slots_is_deterministic(self) -> None:
        self.assertEqual(slots_to_seconds(seconds_to_slots(0.75, 0.25), 0.25), 0.75)


if __name__ == "__main__":
    unittest.main()
