from __future__ import annotations

import unittest

from src.environment.link_rate_config import seconds_to_slots


class ComputationDelaySecondsToSlotsTests(unittest.TestCase):
    def test_seconds_to_slots_supports_paper_delta_and_runtime_values(self) -> None:
        self.assertEqual(seconds_to_slots(0.0, 0.1), 0)
        self.assertEqual(seconds_to_slots(0.05, 0.1), 1)
        self.assertEqual(seconds_to_slots(0.1, 0.1), 1)
        self.assertEqual(seconds_to_slots(0.25, 1.0), 1)


if __name__ == "__main__":
    unittest.main()
