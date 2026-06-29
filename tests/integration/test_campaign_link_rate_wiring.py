from __future__ import annotations

import unittest

from src.analysis.full_training_reproduction_campaign import CampaignConfig
from src.environment.link_rate_config import LinkRateConfig, compute_transmission_delay, mbps_to_bps

PAPER_HORIZONTAL_MBPS = 30.0
PAPER_VERTICAL_MBPS = 10.0
DEFAULT_SLOT_SECONDS = 0.1
KNOWN_TASK_SIZE_BITS = 1_500_000


class CampaignLinkRateWiringTests(unittest.TestCase):
    def test_default_horizontal_rate_is_30_mbps(self) -> None:
        config = CampaignConfig()
        self.assertEqual(config.horizontal_data_rate_mbps, PAPER_HORIZONTAL_MBPS)

    def test_default_vertical_rate_is_10_mbps(self) -> None:
        config = CampaignConfig()
        self.assertEqual(config.vertical_data_rate_mbps, PAPER_VERTICAL_MBPS)

    def test_build_link_rate_config_defaults(self) -> None:
        config = CampaignConfig()
        lrc = config.build_link_rate_config()
        self.assertIsInstance(lrc, LinkRateConfig)
        self.assertEqual(lrc.horizontal_data_rate_mbps, PAPER_HORIZONTAL_MBPS)
        self.assertEqual(lrc.vertical_data_rate_mbps, PAPER_VERTICAL_MBPS)

    def test_build_link_rate_config_custom_values(self) -> None:
        config = CampaignConfig(horizontal_data_rate_mbps=60.0, vertical_data_rate_mbps=20.0)
        lrc = config.build_link_rate_config()
        self.assertEqual(lrc.horizontal_data_rate_mbps, 60.0)
        self.assertEqual(lrc.vertical_data_rate_mbps, 20.0)

    def test_same_task_size_larger_vertical_delay_than_horizontal(self) -> None:
        lrc = LinkRateConfig(
            horizontal_data_rate_mbps=PAPER_HORIZONTAL_MBPS,
            vertical_data_rate_mbps=PAPER_VERTICAL_MBPS,
        )
        horizontal_delay = compute_transmission_delay(
            KNOWN_TASK_SIZE_BITS,
            lrc.horizontal_data_rate_bps,
            slot_duration_seconds=DEFAULT_SLOT_SECONDS,
        )
        vertical_delay = compute_transmission_delay(
            KNOWN_TASK_SIZE_BITS,
            lrc.vertical_data_rate_bps,
            slot_duration_seconds=DEFAULT_SLOT_SECONDS,
        )
        self.assertGreater(vertical_delay.delay_seconds, horizontal_delay.delay_seconds)
        self.assertGreater(vertical_delay.delay_slots, horizontal_delay.delay_slots)

    def test_known_task_size_known_rate_gives_expected_delay(self) -> None:
        task_size_bits = 1_000_000
        rate_mbps = 10.0
        rate_bps = mbps_to_bps(rate_mbps)
        expected_delay_seconds = task_size_bits / rate_bps
        result = compute_transmission_delay(
            task_size_bits,
            rate_bps,
            slot_duration_seconds=DEFAULT_SLOT_SECONDS,
        )
        self.assertAlmostEqual(result.delay_seconds, expected_delay_seconds)
        expected_slots = int(expected_delay_seconds / DEFAULT_SLOT_SECONDS + 0.999999)
        self.assertEqual(result.delay_slots, expected_slots)

    def test_horizontal_rate_from_campaign_config_matches_explicit_link_rate(self) -> None:
        config = CampaignConfig()
        lrc = config.build_link_rate_config()
        payload_bits = 2_000_000
        h_delay = compute_transmission_delay(
            payload_bits,
            lrc.horizontal_data_rate_bps,
            slot_duration_seconds=DEFAULT_SLOT_SECONDS,
        )
        expected_h_delay_seconds = payload_bits / mbps_to_bps(config.horizontal_data_rate_mbps)
        self.assertAlmostEqual(h_delay.delay_seconds, expected_h_delay_seconds)

    def test_vertical_rate_from_campaign_config_matches_explicit_link_rate(self) -> None:
        config = CampaignConfig()
        lrc = config.build_link_rate_config()
        payload_bits = 2_000_000
        v_delay = compute_transmission_delay(
            payload_bits,
            lrc.vertical_data_rate_bps,
            slot_duration_seconds=DEFAULT_SLOT_SECONDS,
        )
        expected_v_delay_seconds = payload_bits / mbps_to_bps(config.vertical_data_rate_mbps)
        self.assertAlmostEqual(v_delay.delay_seconds, expected_v_delay_seconds)

    def test_campaign_config_exposes_link_rate_fields_in_to_dict(self) -> None:
        config = CampaignConfig()
        d = config.to_dict()
        self.assertEqual(d["horizontal_data_rate_mbps"], PAPER_HORIZONTAL_MBPS)
        self.assertEqual(d["vertical_data_rate_mbps"], PAPER_VERTICAL_MBPS)


class CampaignConfigLinkRateValidationTests(unittest.TestCase):
    def test_rejects_non_positive_horizontal_rate(self) -> None:
        with self.assertRaises(ValueError):
            CampaignConfig(horizontal_data_rate_mbps=0)
        with self.assertRaises(ValueError):
            CampaignConfig(horizontal_data_rate_mbps=-5.0)

    def test_rejects_non_positive_vertical_rate(self) -> None:
        with self.assertRaises(ValueError):
            CampaignConfig(vertical_data_rate_mbps=0)
        with self.assertRaises(ValueError):
            CampaignConfig(vertical_data_rate_mbps=-5.0)


if __name__ == "__main__":
    unittest.main()
