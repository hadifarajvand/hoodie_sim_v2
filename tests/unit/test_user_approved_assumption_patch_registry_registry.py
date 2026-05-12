from __future__ import annotations

import unittest

from src.analysis.user_approved_assumption_patch_registry.registry import build_registry_entries


class UserApprovedAssumptionPatchRegistryRegistryTest(unittest.TestCase):
    def test_entries_have_required_semantic_fields(self) -> None:
        entries = build_registry_entries()
        for entry in entries:
            payload = entry.to_dict()
            self.assertTrue(payload["no_paper_recovery_claim"])
            self.assertTrue(str(payload["rationale"]).strip())
            self.assertTrue(str(payload["scientific_risk"]).strip())
            self.assertTrue(str(payload["validation_plan"]).strip())
            self.assertIsInstance(payload["affected_runtime_components"], list)
            self.assertGreater(len(payload["affected_runtime_components"]), 0)

    def test_initial_statuses_match_feature_031_policy(self) -> None:
        entries = {entry.item_id: entry for entry in build_registry_entries()}
        self.assertEqual(entries["Figure_7_adjacency"].assumption_status, "blocked_no_assumption")
        self.assertEqual(entries["legal_horizontal_destinations"].assumption_status, "blocked_no_assumption")
        self.assertEqual(entries["timeout_value"].assumption_status, "blocked_no_assumption")
        for item_id in [
            "EA_private_cpu_capacity",
            "EA_public_cpu_capacity",
            "cloud_cpu_capacity",
            "cloud_data_rate",
            "multi_agent_aggregation_reduction_order",
        ]:
            self.assertEqual(entries[item_id].assumption_status, "proposed")
            self.assertFalse(entries[item_id].runtime_use_allowed)
            self.assertTrue(entries[item_id].approval_required)

    def test_runtime_use_requires_approved_status(self) -> None:
        entries = build_registry_entries()
        self.assertFalse(any(entry.runtime_use_allowed for entry in entries))
        self.assertTrue(all(entry.assumption_status != "approved" for entry in entries))

    def test_semantic_fields_reject_empty_values(self) -> None:
        from src.analysis.user_approved_assumption_patch_registry.report import _validate_non_empty_fields

        with self.assertRaises(ValueError):
            _validate_non_empty_fields(
                [
                    {
                        "item_id": "broken",
                        "rationale": "",
                        "scientific_risk": "risk",
                        "affected_runtime_components": ["x"],
                        "validation_plan": "plan",
                    }
                ]
            )


if __name__ == "__main__":
    unittest.main()
