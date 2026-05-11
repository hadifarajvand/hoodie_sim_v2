from __future__ import annotations

import unittest

from src.analysis.link_rate_transmission_delay_contract.report import build_link_rate_contract_report
from src.environment.link_rate_config import LinkRateConfig, compute_transmission_delay, mbps_to_bps


class Feature027RegressionTests(unittest.TestCase):
    def test_link_rate_transmission_delay_formula_and_monotonicity_remain_intact(self) -> None:
        report = build_link_rate_contract_report().to_dict()
        self.assertEqual(report["transmission_delay_contract"]["slot_duration_seconds"], 0.1)

        lower = compute_transmission_delay(8_000_000.0, mbps_to_bps(30.0), slot_duration_seconds=0.1)
        higher = compute_transmission_delay(8_000_000.0, mbps_to_bps(60.0), slot_duration_seconds=0.1)
        self.assertLessEqual(higher.delay_seconds, lower.delay_seconds)
        self.assertLessEqual(higher.delay_slots, lower.delay_slots)

    def test_public_link_rate_defaults_are_preserved(self) -> None:
        config = LinkRateConfig()
        self.assertEqual(config.horizontal_data_rate_mbps, 30.0)
        self.assertEqual(config.vertical_data_rate_mbps, 10.0)
        self.assertEqual(config.slot_duration_seconds, 0.1)


if __name__ == "__main__":
    unittest.main()
