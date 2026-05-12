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

    def test_runtime_approved_item_is_confined_to_figure_7(self) -> None:
        report = build_assumption_patch_report().to_dict()
        self.assertEqual([item["item_id"] for item in report["runtime_usable_items"]], ["Figure_7_adjacency", "legal_horizontal_destinations", "EA_private_cpu_capacity", "EA_public_cpu_capacity", "cloud_cpu_capacity", "cloud_data_rate", "timeout_value", "multi_agent_aggregation_reduction_order"])
        self.assertEqual(report["status_counts"]["approved"], 8)
        self.assertEqual(report["final_verdict"], "registry_created_with_runtime_approved_assumptions")


if __name__ == "__main__":
    unittest.main()
