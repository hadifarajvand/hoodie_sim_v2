from __future__ import annotations

import unittest

from src.environment.link_rate_config import LinkRateConfig, compute_transmission_delay


class LinkRateInvalidInputTests(unittest.TestCase):
    def test_invalid_rates_fail_loudly(self) -> None:
        with self.assertRaises(ValueError):
            LinkRateConfig(horizontal_data_rate_mbps=0.0)
        with self.assertRaises(ValueError):
            LinkRateConfig(vertical_data_rate_mbps=-1.0)
        with self.assertRaises(ValueError):
            compute_transmission_delay(8.0, 0.0, slot_duration_seconds=1.0)
        with self.assertRaises(ValueError):
            compute_transmission_delay(8.0, -1.0, slot_duration_seconds=1.0)

    def test_invalid_payloads_fail_loudly_and_zero_payload_is_explicit(self) -> None:
        with self.assertRaises(ValueError):
            compute_transmission_delay(-1.0, 1.0, slot_duration_seconds=1.0)

        zero = compute_transmission_delay(0.0, 1.0, slot_duration_seconds=1.0)
        self.assertEqual(zero.delay_seconds, 0.0)
        self.assertEqual(zero.delay_slots, 0)
        self.assertEqual(zero.zero_payload_policy, "explicit_zero_delay")


if __name__ == "__main__":
    unittest.main()
