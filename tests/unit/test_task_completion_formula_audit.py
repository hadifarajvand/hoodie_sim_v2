from __future__ import annotations

import unittest

from src.analysis.task_completion_lifecycle_formula_audit import CompletionLifecycleAuditConfig, FormulaAuditCalculator


class TaskCompletionFormulaAuditUnitTests(unittest.TestCase):
    def test_paper_default_config_contract(self) -> None:
        config = CompletionLifecycleAuditConfig()
        self.assertEqual(config.feature_id, "043-task-completion-lifecycle-formula-audit")
        self.assertEqual(config.episode_length, 110)
        self.assertEqual(config.timeout_slots, 20)
        self.assertEqual(config.arrival_probability, 0.5)
        self.assertEqual(config.node_count, 20)
        self.assertEqual(config.task_size_range_mbits, (2.0, 5.0))
        self.assertEqual(config.processing_density_gcycles_per_mbit, 0.297)
        self.assertEqual(config.horizontal_rate_mbps, 30.0)
        self.assertEqual(config.vertical_rate_mbps, 10.0)
        self.assertEqual(list(config.seeds), [0, 1, 2])

    def test_formula_examples_match_hand_calculation(self) -> None:
        calc = FormulaAuditCalculator()
        example_2 = calc.build_estimate(2.0)
        example_5 = calc.build_estimate(5.0)
        self.assertAlmostEqual(example_2.task_cycles_gcycles, 0.594)
        self.assertEqual(example_2.local_compute_slots, 2)
        self.assertEqual(example_2.public_compute_slots, 2)
        self.assertEqual(example_2.cloud_compute_slots, 1)
        self.assertEqual(example_2.horizontal_transmission_slots, 1)
        self.assertEqual(example_2.vertical_transmission_slots, 2)
        self.assertEqual(example_2.local_min_total_slots, 2)
        self.assertEqual(example_2.horizontal_min_total_slots, 3)
        self.assertEqual(example_2.vertical_min_total_slots, 3)
        self.assertAlmostEqual(example_5.task_cycles_gcycles, 1.485)
        self.assertEqual(example_5.local_compute_slots, 3)
        self.assertEqual(example_5.public_compute_slots, 3)
        self.assertEqual(example_5.cloud_compute_slots, 1)
        self.assertEqual(example_5.horizontal_transmission_slots, 2)
        self.assertEqual(example_5.vertical_transmission_slots, 5)
        self.assertEqual(example_5.local_min_total_slots, 3)
        self.assertEqual(example_5.horizontal_min_total_slots, 5)
        self.assertEqual(example_5.vertical_min_total_slots, 6)

    def test_rounding_convention_is_ceil(self) -> None:
        calc = FormulaAuditCalculator()
        self.assertEqual(calc.compute_transmission_slots(2.0, 30.0), 1)
        self.assertEqual(calc.compute_transmission_slots(5.0, 10.0), 5)


if __name__ == "__main__":
    unittest.main()
