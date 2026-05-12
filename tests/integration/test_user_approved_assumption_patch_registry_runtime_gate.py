from __future__ import annotations

import unittest

from src.analysis.user_approved_assumption_patch_registry.registry import build_registry_entries


class UserApprovedAssumptionPatchRegistryRuntimeGateTest(unittest.TestCase):
    def test_runtime_use_only_possible_for_approved_assumptions(self) -> None:
        entries = build_registry_entries()
        self.assertEqual(sum(1 for entry in entries if entry.runtime_use_allowed), 3)
        approved = [entry for entry in entries if entry.assumption_status == "approved"]
        self.assertEqual([entry.item_id for entry in approved], ["Figure_7_adjacency", "legal_horizontal_destinations", "EA_private_cpu_capacity"])
        self.assertTrue(all(entry.runtime_use_allowed for entry in approved))
        self.assertFalse(any(entry.runtime_use_allowed for entry in entries if entry.item_id not in {"Figure_7_adjacency", "legal_horizontal_destinations", "EA_private_cpu_capacity"}))


if __name__ == "__main__":
    unittest.main()
