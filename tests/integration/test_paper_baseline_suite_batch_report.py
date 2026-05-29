from __future__ import annotations

import json
from pathlib import Path
import unittest

from src.analysis.paper_baseline_suite_batch import build_paper_baseline_suite_batch_report


class PaperBaselineSuiteBatchReportTests(unittest.TestCase):
    def test_artifacts_written(self) -> None:
        build_paper_baseline_suite_batch_report()
        path = Path("artifacts/analysis/paper-baseline-suite-batch/paper-baseline-suite-batch-report.json")
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["feature_067_verified"], True)


if __name__ == "__main__":
    unittest.main()

