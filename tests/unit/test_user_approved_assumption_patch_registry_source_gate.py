from __future__ import annotations

import unittest

from src.analysis.user_approved_assumption_patch_registry.registry import (
    SOURCE_GATE_TAG,
    build_registry_entries,
    load_feature_030_closure_report,
    validate_source_gate,
)


class UserApprovedAssumptionPatchRegistrySourceGateTest(unittest.TestCase):
    def test_source_gate_validates_feature_030_tag_and_report(self) -> None:
        gate = validate_source_gate()
        self.assertEqual(gate["source_gate_tag"], SOURCE_GATE_TAG)
        self.assertTrue(gate["tag_present"])
        self.assertTrue(gate["source_report"].endswith("assumption-closure-report.json"))

    def test_registry_covers_exact_candidates_once(self) -> None:
        report = load_feature_030_closure_report()
        entries = build_registry_entries()

        self.assertGreater(len(report["items"]), len(entries))
        self.assertEqual(
            [entry.item_id for entry in entries],
            [
                "Figure_7_adjacency",
                "legal_horizontal_destinations",
                "EA_private_cpu_capacity",
                "EA_public_cpu_capacity",
                "cloud_cpu_capacity",
                "cloud_data_rate",
                "timeout_value",
                "multi_agent_aggregation_reduction_order",
            ],
        )

        closure_index = {item["item_id"]: item for item in report["items"]}
        for entry in entries:
            self.assertIn(entry.item_id, closure_index)
            self.assertEqual(entry.paper_status, closure_index[entry.item_id]["status"])
            self.assertEqual(entry.paper_confidence, closure_index[entry.item_id]["confidence"])


if __name__ == "__main__":
    unittest.main()
