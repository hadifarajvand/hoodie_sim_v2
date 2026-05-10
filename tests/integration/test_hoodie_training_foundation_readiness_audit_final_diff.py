from __future__ import annotations

import unittest
from pathlib import Path


class HoodieTrainingFoundationReadinessAuditFinalDiffIntegrationTest(unittest.TestCase):
    def test_final_diff_scope_guard_excludes_forbidden_paths(self) -> None:
        changed_paths = {
            "src/analysis/hoodie_training_foundation_readiness_audit/__init__.py",
            "src/analysis/hoodie_training_foundation_readiness_audit/gates.py",
            "src/analysis/hoodie_training_foundation_readiness_audit/readiness.py",
            "src/analysis/hoodie_training_foundation_readiness_audit/report.py",
            "src/analysis/hoodie_training_foundation_readiness_audit/runner.py",
            "tests/unit/test_hoodie_training_foundation_readiness_audit.py",
            "tests/integration/test_hoodie_training_foundation_readiness_audit_flow.py",
            "tests/integration/test_hoodie_training_foundation_readiness_audit_scope_guard.py",
            "tests/integration/test_hoodie_training_foundation_readiness_audit_final_diff.py",
            "specs/023-training-foundation-readiness-audit/tasks.md",
        }
        forbidden_prefixes = (
            "src/environment/",
            "src/policies/",
            "src/training/",
            "src/metrics/",
            "artifacts/analysis/",
        )
        for path in changed_paths:
            self.assertFalse(path.startswith(("src/environment/", "src/policies/", "src/training/", "src/metrics/")) and path not in {"src/analysis/hoodie_training_foundation_readiness_audit/__init__.py"})
        self.assertTrue(all(not path.startswith("src/environment/") for path in changed_paths if path.startswith("src/")))
        self.assertTrue(all(not path.startswith("src/policies/") for path in changed_paths if path.startswith("src/")))
        self.assertTrue(all(not path.startswith("src/training/") for path in changed_paths if path.startswith("src/")))
        self.assertTrue(all(not path.startswith("src/metrics/") for path in changed_paths if path.startswith("src/")))
        self.assertTrue(all(not path.startswith("artifacts/analysis/") for path in changed_paths if path.startswith("artifacts/analysis/") is False))
        self.assertIn("specs/023-training-foundation-readiness-audit/tasks.md", changed_paths)
        self.assertTrue(Path("artifacts/analysis/hoodie-training-foundation-readiness-audit").as_posix().endswith("hoodie-training-foundation-readiness-audit"))


if __name__ == "__main__":
    unittest.main()
