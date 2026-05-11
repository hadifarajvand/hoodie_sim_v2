from __future__ import annotations

import unittest

from src.analysis.computation_delay_cpu_unit_validation.report import build_unit_validation_report


class ComputationDelayScopeGuardTests(unittest.TestCase):
    def test_forbidden_changes_are_not_claimed(self) -> None:
        report = build_unit_validation_report().to_dict()
        self.assertTrue(report["no_curve_fitting"])
        self.assertTrue(report["no_policy_or_training_drift"])
        self.assertEqual(report["cpu_capacity_contract"]["EA_private"]["status"], "unrecoverable")
        self.assertEqual(report["cpu_capacity_contract"]["EA_public"]["status"], "unrecoverable")
        self.assertEqual(report["cpu_capacity_contract"]["cloud"]["status"], "unrecoverable")


if __name__ == "__main__":
    unittest.main()
