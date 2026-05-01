from __future__ import annotations

import unittest

from src.environment.compute_config import ComputeConfig


class ComputeConfigTests(unittest.TestCase):
    def test_default_compute_capacities_are_deterministic(self) -> None:
        config = ComputeConfig()

        self.assertEqual(config.cpu_capacity_per_slot_agent, 32.0)
        self.assertEqual(config.cpu_capacity_per_slot_edge, 64.0)
        self.assertEqual(config.cpu_capacity_per_slot_cloud, 128.0)
        self.assertEqual(config.capacity_for("local"), 32.0)
        self.assertEqual(config.capacity_for("public"), 64.0)
        self.assertEqual(config.capacity_for("cloud"), 128.0)

    def test_invalid_capacity_values_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ComputeConfig(cpu_capacity_per_slot_agent=0.0)
        with self.assertRaises(ValueError):
            ComputeConfig(cpu_capacity_per_slot_edge=-1.0)
        with self.assertRaises(ValueError):
            ComputeConfig(cpu_capacity_per_slot_cloud=0.0)

    def test_unsupported_destination_is_rejected(self) -> None:
        config = ComputeConfig()

        with self.assertRaises(ValueError):
            config.capacity_for("stochastic")


if __name__ == "__main__":
    unittest.main()
