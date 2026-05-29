from __future__ import annotations

import json
from pathlib import Path
import unittest

from src.analysis.full_hoodie_mechanism_fidelity_batch import build_full_hoodie_mechanism_fidelity_batch_report


class FullHOODIEMechanismFidelityBatchReportTests(unittest.TestCase):
    def test_artifacts_written(self) -> None:
        build_full_hoodie_mechanism_fidelity_batch_report()
        path = Path("artifacts/analysis/full-hoodie-mechanism-fidelity-batch/full-hoodie-mechanism-fidelity-batch-report.json")
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(payload["distributed_coordination_enabled"])


if __name__ == "__main__":
    unittest.main()

