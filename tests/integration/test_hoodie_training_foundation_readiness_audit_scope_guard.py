from __future__ import annotations

import unittest
from pathlib import Path


class HoodieTrainingFoundationReadinessAuditScopeGuardIntegrationTest(unittest.TestCase):
    def test_feature_outputs_are_namespaced_and_forbidden_paths_are_not_targeted(self) -> None:
        output_dir = Path("artifacts/analysis/hoodie-training-foundation-readiness-audit")
        self.assertEqual(output_dir.as_posix(), "artifacts/analysis/hoodie-training-foundation-readiness-audit")
        forbidden = {
            "src/environment",
            "src/policies",
            "src/training",
            "src/metrics",
            "dependency files",
            "lockfiles",
            "existing campaign artifacts",
            "TorchRL",
            "Gymnasium",
            "ns-3",
            "ns-3-gym",
        }
        self.assertIn("src/training", forbidden)
        self.assertIn("artifacts/analysis/hoodie-training-foundation-readiness-audit", output_dir.as_posix())


if __name__ == "__main__":
    unittest.main()
