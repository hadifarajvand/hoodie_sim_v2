from __future__ import annotations

import unittest

from src.baselines import MinimumLatencyEstimationOffloader


class MLEOPolicyTests(unittest.TestCase):
    def test_selects_minimum_latency_destination(self) -> None:
        policy = MinimumLatencyEstimationOffloader()
        choice = policy.select(
            legal_destination_ids=["local", "6", "cloud"],
            queue_delay={"local": 10.0, "6": 2.0, "cloud": 1.0},
            transmission_delay={"local": 1.0, "6": 1.0, "cloud": 0.5},
            waiting_time={"local": 1.0, "6": 0.0, "cloud": 0.0},
            forecast_load={"local": 1.0, "6": 0.5, "cloud": 0.0},
        )
        self.assertEqual(choice, "cloud")


if __name__ == "__main__":
    unittest.main()
