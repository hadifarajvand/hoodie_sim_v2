from __future__ import annotations

import unittest

from src.analysis.user_approved_assumption_patch_registry.report import build_assumption_patch_report
from src.analysis.user_approved_assumption_patch_registry.registry import build_user_approved_assumption_registry


class UserApprovedAssumptionPatchRegistryDeterminismTest(unittest.TestCase):
    def test_registry_and_report_are_deterministic(self) -> None:
        registry_one = build_user_approved_assumption_registry()
        registry_two = build_user_approved_assumption_registry()
        self.assertEqual(registry_one, registry_two)

        report_one = build_assumption_patch_report().to_dict()
        report_two = build_assumption_patch_report().to_dict()
        self.assertEqual(report_one, report_two)

    def test_no_approved_items_and_report_only_proposals(self) -> None:
        report = build_assumption_patch_report().to_dict()
        self.assertEqual(report["runtime_usable_items"], [])
        self.assertEqual(report["status_counts"]["approved"], 0)
        self.assertEqual(report["final_verdict"], "registry_created_no_runtime_approved_assumptions")


if __name__ == "__main__":
    unittest.main()
