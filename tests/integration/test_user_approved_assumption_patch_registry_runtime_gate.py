from __future__ import annotations

import unittest

from src.analysis.user_approved_assumption_patch_registry.registry import build_registry_entries


class UserApprovedAssumptionPatchRegistryRuntimeGateTest(unittest.TestCase):
    def test_runtime_use_only_possible_for_approved_assumptions(self) -> None:
        for entry in build_registry_entries():
            self.assertFalse(entry.runtime_use_allowed)
            self.assertNotEqual(entry.assumption_status, "approved")


if __name__ == "__main__":
    unittest.main()
