from __future__ import annotations

import unittest

from src.analysis.user_approved_assumption_patch_registry.registry import build_registry_entries


class UserApprovedAssumptionPatchRegistryRuntimeGateTest(unittest.TestCase):
    def test_runtime_use_only_possible_for_approved_assumptions(self) -> None:
        entries = build_registry_entries()
        self.assertEqual(sum(1 for entry in entries if entry.runtime_use_allowed), 1)
        approved = [entry for entry in entries if entry.assumption_status == "approved"]
        self.assertEqual(len(approved), 1)
        self.assertEqual(approved[0].item_id, "Figure_7_adjacency")
        self.assertTrue(approved[0].runtime_use_allowed)
        self.assertFalse(any(entry.runtime_use_allowed for entry in entries if entry.item_id != "Figure_7_adjacency"))


if __name__ == "__main__":
    unittest.main()
