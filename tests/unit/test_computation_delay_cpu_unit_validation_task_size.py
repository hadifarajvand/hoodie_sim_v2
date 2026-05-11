from __future__ import annotations

import unittest

from src.analysis.computation_delay_cpu_unit_validation.unit_evidence import build_paper_unit_evidence


class ComputationDelayTaskSizeTests(unittest.TestCase):
    def test_task_size_units_are_recovered_as_mbits(self) -> None:
        evidence = build_paper_unit_evidence()["task_size"]
        self.assertEqual(evidence["status"], "recovered")
        self.assertEqual(evidence["unit"], "Mbits")
        self.assertEqual(evidence["value"], "[2,2.1,...,5] Mbits")


if __name__ == "__main__":
    unittest.main()
