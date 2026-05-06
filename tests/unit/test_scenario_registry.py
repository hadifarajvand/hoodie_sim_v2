from __future__ import annotations

import unittest

from src.evaluation.scenario_registry import ScenarioRegistry
from src.environment.traffic_config import TrafficScenarioPreset


class ScenarioRegistryTests(unittest.TestCase):
    def test_all_scenarios_are_registered(self) -> None:
        self.assertEqual(
            ScenarioRegistry.supported_names(),
            ("paper_default", "moderate", "heavy", "extreme"),
        )
        self.assertEqual(ScenarioRegistry.resolve("paper_default").scenario_name, TrafficScenarioPreset.paper_default().scenario_name)
        self.assertEqual(ScenarioRegistry.resolve("moderate").scenario_name, "moderate")
        self.assertEqual(ScenarioRegistry.resolve("heavy").scenario_name, "heavy")
        self.assertEqual(ScenarioRegistry.resolve("extreme").scenario_name, "extreme")

    def test_episode_length_override_applies_only_when_provided(self) -> None:
        config = ScenarioRegistry.resolve("moderate", episode_length_override=12)
        self.assertEqual(config.episode_length, 12)

    def test_unsupported_scenario_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ScenarioRegistry.resolve("unknown")


if __name__ == "__main__":
    unittest.main()
