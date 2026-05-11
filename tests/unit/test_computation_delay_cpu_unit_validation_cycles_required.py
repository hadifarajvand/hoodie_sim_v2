from __future__ import annotations

import unittest

from src.analysis.computation_delay_cpu_unit_validation.computation_delay import compute_cycles_required


class ComputationDelayCyclesRequiredTests(unittest.TestCase):
    def test_cycles_required_formula_is_deterministic(self) -> None:
        self.assertAlmostEqual(compute_cycles_required(2.1, 0.297), 2.1 * 0.297)
        self.assertAlmostEqual(compute_cycles_required(5.0, 0.297), 5.0 * 0.297)


if __name__ == "__main__":
    unittest.main()
