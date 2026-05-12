from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


class UserApprovedAssumptionPatchRegistryScopeGuardTest(unittest.TestCase):
    def test_git_diff_scope_contains_only_feature_031_changes(self) -> None:
        result = subprocess.run(
            ["git", "diff", "--name-only"],
            cwd=Path.cwd(),
            check=True,
            capture_output=True,
            text=True,
        )
        changed = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        allowed_prefixes = (
            "src/analysis/user_approved_assumption_patch_registry/",
            "tests/unit/test_user_approved_assumption_patch_registry_",
            "tests/integration/test_user_approved_assumption_patch_registry_",
            "resources/papers/hoodie/recovered/user-approved-assumption-registry.json",
            "artifacts/analysis/user-approved-assumption-patch-registry/",
            ".specify/memory/constitution.md",
            "docs/reproducibility.md",
        )
        for path in changed:
            self.assertTrue(path.startswith(allowed_prefixes), path)


if __name__ == "__main__":
    unittest.main()
