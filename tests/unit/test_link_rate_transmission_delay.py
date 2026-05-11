from __future__ import annotations

import unittest

from src.environment.link_rate_config import compute_transmission_delay, mbps_to_bps


class LinkRateTransmissionDelayTests(unittest.TestCase):
    def test_formula_matches_payload_over_rate(self) -> None:
        result = compute_transmission_delay(8_000_000.0, mbps_to_bps(8.0), slot_duration_seconds=0.5)
        self.assertEqual(result.delay_seconds, 1.0)
        self.assertEqual(result.delay_slots, 2)
        self.assertEqual(result.slot_rounding_policy, "ceil")
        self.assertEqual(result.payload_unit, "bits")
        self.assertEqual(result.rate_unit, "bps")


if __name__ == "__main__":
    unittest.main()
