from __future__ import annotations

import unittest

from src.analysis.computation_delay_cpu_unit_validation.unit_evidence import build_paper_unit_evidence


class ComputationDelayProcessingDensityTests(unittest.TestCase):
    def test_processing_density_units_are_recovered_as_gigacycles_per_mbit(self) -> None:
        evidence = build_paper_unit_evidence()["processing_density"]
        self.assertEqual(evidence["status"], "recovered")
        self.assertEqual(evidence["unit"], "gigacycles/Mbit")
        self.assertEqual(evidence["value"], "0.297 gigacycles/Mbit")


if __name__ == "__main__":
    unittest.main()
