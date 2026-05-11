from __future__ import annotations

import unittest

from src.environment.gym_adapter import HoodieGymEnvironment
from src.environment.link_rate_config import LinkRateConfig


class LinkRateControlHorizontalIntegrationTest(unittest.TestCase):
    def test_horizontal_data_rate_is_publicly_configurable(self) -> None:
        config = LinkRateConfig(horizontal_data_rate_mbps=45.0, vertical_data_rate_mbps=10.0, slot_duration_seconds=0.5)
        env = HoodieGymEnvironment(episode_length=2, link_rate_config=config)
        _, info = env.reset(seed=7)
        self.assertEqual(env.link_rate_config.horizontal_data_rate_mbps, 45.0)
        self.assertEqual(info["link_rate_config"]["horizontal_data_rate_mbps"], 45.0)
        self.assertEqual(info["link_rate_config"]["public_config_entrypoint"], "src/environment/link_rate_config.py")


if __name__ == "__main__":
    unittest.main()
