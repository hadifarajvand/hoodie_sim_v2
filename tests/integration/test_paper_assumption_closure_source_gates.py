from __future__ import annotations

import unittest
from pathlib import Path

from src.analysis.paper_assumption_closure_evidence_exhaustion.source_loader import SOURCE_GATE_PATHS


class PaperAssumptionClosureSourceGateTests(unittest.TestCase):
    def test_required_artifact_paths_are_declared(self) -> None:
        self.assertGreater(len(SOURCE_GATE_PATHS), 0)
        for path in SOURCE_GATE_PATHS:
            self.assertIsInstance(path, Path)

