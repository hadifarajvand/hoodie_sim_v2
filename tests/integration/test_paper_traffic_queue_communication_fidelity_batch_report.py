from __future__ import annotations

import json
from pathlib import Path
import unittest

from src.analysis.paper_traffic_queue_communication_fidelity_batch import build_paper_traffic_queue_communication_fidelity_batch_report


class PaperTrafficQueueCommunicationFidelityBatchReportTests(unittest.TestCase):
    def test_artifacts_written(self) -> None:
        build_paper_traffic_queue_communication_fidelity_batch_report()
        path = Path("artifacts/analysis/paper-traffic-queue-communication-fidelity-batch/paper-traffic-queue-communication-fidelity-batch-report.json")
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["feature_id"], "067-paper-traffic-queue-communication-fidelity-batch")


if __name__ == "__main__":
    unittest.main()

