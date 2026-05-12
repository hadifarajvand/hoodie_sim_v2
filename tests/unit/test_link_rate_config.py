from __future__ import annotations

import unittest

from src.environment.link_rate_config import LinkRateConfig, compute_transmission_delay, mbits_to_bits


class LinkRateConfigTests(unittest.TestCase):
    def test_compute_transmission_delay_uses_configured_rounding_policy(self) -> None:
        config = LinkRateConfig(
            horizontal_data_rate_mbps=30.0,
            vertical_data_rate_mbps=10.0,
            slot_duration_seconds=0.1,
            rounding_policy="floor",
        )
        payload_bits = mbits_to_bits(1.5)

        result = compute_transmission_delay(
            payload_bits,
            config.horizontal_data_rate_bps,
            slot_duration_seconds=config.slot_duration_seconds,
            rounding_policy=config.rounding_policy,
        )

        self.assertEqual(result.payload_bits, payload_bits)
        self.assertEqual(result.data_rate_bps, config.horizontal_data_rate_bps)
        self.assertEqual(result.delay_seconds, 0.05)
        self.assertEqual(result.delay_slots, 0)
        self.assertEqual(result.slot_rounding_policy, "floor")

    def test_zero_payload_has_explicit_zero_delay(self) -> None:
        config = LinkRateConfig()

        result = compute_transmission_delay(
            0.0,
            config.vertical_data_rate_bps,
            slot_duration_seconds=config.slot_duration_seconds,
            rounding_policy=config.rounding_policy,
        )

        self.assertEqual(result.delay_seconds, 0.0)
        self.assertEqual(result.delay_slots, 0)


if __name__ == "__main__":
    unittest.main()

