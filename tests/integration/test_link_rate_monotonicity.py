from __future__ import annotations

import unittest

from src.environment.link_rate_config import compute_transmission_delay, mbps_to_bps


class LinkRateMonotonicityIntegrationTest(unittest.TestCase):
    def test_increasing_horizontal_data_rate_does_not_increase_delay(self) -> None:
        payload_bits = 8_000_000.0
        lower = compute_transmission_delay(payload_bits, mbps_to_bps(30.0), slot_duration_seconds=1.0)
        higher = compute_transmission_delay(payload_bits, mbps_to_bps(60.0), slot_duration_seconds=1.0)
        self.assertLessEqual(higher.delay_seconds, lower.delay_seconds)
        self.assertLessEqual(higher.delay_slots, lower.delay_slots)

    def test_increasing_vertical_data_rate_does_not_increase_delay(self) -> None:
        payload_bits = 8_000_000.0
        lower = compute_transmission_delay(payload_bits, mbps_to_bps(10.0), slot_duration_seconds=1.0)
        higher = compute_transmission_delay(payload_bits, mbps_to_bps(20.0), slot_duration_seconds=1.0)
        self.assertLessEqual(higher.delay_seconds, lower.delay_seconds)
        self.assertLessEqual(higher.delay_slots, lower.delay_slots)


if __name__ == "__main__":
    unittest.main()
