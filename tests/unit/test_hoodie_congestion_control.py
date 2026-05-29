from __future__ import annotations

import unittest

from src.environment.hoodie_congestion_control import HoodieCongestionControl


class HoodieCongestionControlTests(unittest.TestCase):
    def test_overloaded_nodes_are_masked_and_cloud_can_remain(self) -> None:
        control = HoodieCongestionControl(True, 0.75, True, True)
        mask = control.get_dynamic_mask(base_mask=[True, True, True, True, True], queue_pressure={"local": 0.9, "6": 0.9, "11": 0.9})
        self.assertTrue(mask[-1])
        self.assertFalse(mask[1])


if __name__ == "__main__":
    unittest.main()

