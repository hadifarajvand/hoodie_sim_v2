from __future__ import annotations

import unittest

from src.analysis.computation_delay_cpu_unit_validation.completion_slot import compute_completion_slot


class ComputationDelayCompletionSlotTests(unittest.TestCase):
    def test_completion_slot_calculation_is_explicit(self) -> None:
        contract = compute_completion_slot(current_slot=10, cycles_required=6.0, cpu_capacity_per_slot=3.0)
        self.assertEqual(contract.delay_slots, 2)
        self.assertEqual(contract.completion_slot, 12)
        self.assertEqual(contract.zero_delay_policy, "explicit_zero_delay")
        self.assertIn("completion_slot = current_slot + delay_slots", contract.formula)

    def test_zero_delay_is_explicit(self) -> None:
        contract = compute_completion_slot(current_slot=5, cycles_required=0.0, cpu_capacity_per_slot=3.0)
        self.assertEqual(contract.delay_slots, 0)
        self.assertEqual(contract.completion_slot, 5)


if __name__ == "__main__":
    unittest.main()
