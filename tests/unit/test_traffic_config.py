from __future__ import annotations

import unittest

from src.environment.traffic_config import TrafficConfig, TrafficScenarioPreset


class TrafficConfigTests(unittest.TestCase):
    def test_paper_default_preset_values(self) -> None:
        config = TrafficScenarioPreset.paper_default()

        self.assertEqual(config.scenario_name, "paper_default")
        self.assertEqual(config.number_of_agents, 20)
        self.assertEqual(config.episode_length, 110)
        self.assertEqual(config.arrival_probability, 0.5)
        self.assertEqual(config.slot_duration_seconds, 0.1)
        self.assertEqual(config.timeout_slots, 20)
        self.assertEqual(config.task_size_mbits_min, 2.0)
        self.assertEqual(config.task_size_mbits_max, 5.0)
        self.assertEqual(config.task_size_mbits_step, 0.1)
        self.assertEqual(config.processing_density_gcycles_per_mbit, 0.297)
        self.assertEqual(config.task_size_values[0], 2.0)
        self.assertEqual(config.task_size_values[-1], 5.0)

    def test_moderate_heavy_and_extreme_presets(self) -> None:
        moderate = TrafficScenarioPreset.moderate()
        heavy = TrafficScenarioPreset.heavy()
        extreme = TrafficScenarioPreset.extreme()

        self.assertEqual((moderate.arrival_probability, moderate.task_size_mbits_min, moderate.task_size_mbits_max), (0.5, 1.0, 3.0))
        self.assertEqual((heavy.arrival_probability, heavy.task_size_mbits_min, heavy.task_size_mbits_max), (0.7, 2.0, 5.0))
        self.assertEqual((extreme.arrival_probability, extreme.task_size_mbits_min, extreme.task_size_mbits_max), (0.9, 3.0, 7.0))

    def test_invalid_scenario_name_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            TrafficConfig(
                scenario_name="unsupported",
                number_of_agents=20,
                episode_length=110,
                arrival_probability=0.5,
                slot_duration_seconds=0.1,
                timeout_slots=20,
                task_size_mbits_min=2.0,
                task_size_mbits_max=5.0,
                task_size_mbits_step=0.1,
                processing_density_gcycles_per_mbit=0.297,
            )


if __name__ == "__main__":
    unittest.main()
