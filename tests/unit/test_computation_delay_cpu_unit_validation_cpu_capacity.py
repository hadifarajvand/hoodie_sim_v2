from __future__ import annotations

import unittest

from src.analysis.computation_delay_cpu_unit_validation.cpu_capacity import build_cpu_capacity_contract


class ComputationDelayCpuCapacityTests(unittest.TestCase):
    def test_cpu_capacities_remain_unrecoverable(self) -> None:
        contract = build_cpu_capacity_contract()
        for key in ("EA_private", "EA_public", "cloud"):
            self.assertEqual(contract[key]["status"], "unrecoverable")
            self.assertIsNone(contract[key]["value"])


if __name__ == "__main__":
    unittest.main()
