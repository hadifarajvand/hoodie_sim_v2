from __future__ import annotations

import json
from pathlib import Path
import unittest


class OffloadInstrumentationSourceGatesTest(unittest.TestCase):
    def test_feature_gates_and_current_audit_exist(self) -> None:
        root = Path("/Users/hadi/Documents/GitHub/hoodie_sim_v2")
        self.assertTrue((root / "artifacts/analysis/differential-environment-audit/differential-audit.json").exists())
        self.assertTrue((root / "artifacts/analysis/differential-environment-audit/differential-audit.md").exists())
        self.assertTrue((root / "specs/019-mechanism-repair").exists())
        self.assertTrue((root / "specs/024-environment-lifecycle-divergence-repair").exists())
        self.assertTrue((root / "specs/025-structured-paper-topology-linkrate-registry").exists())
        self.assertTrue((root / "specs/026-horizontal-vertical-offload-lifecycle-instrumentation/tasks.md").exists())
        payload = json.loads((root / "artifacts/analysis/differential-environment-audit/differential-audit.json").read_text())
        self.assertIn("comparison_results", payload)
