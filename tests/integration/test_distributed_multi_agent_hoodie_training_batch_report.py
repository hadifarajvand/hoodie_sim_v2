from __future__ import annotations

import json
from pathlib import Path
import unittest

from src.analysis.distributed_multi_agent_hoodie_training_batch import build_distributed_multi_agent_hoodie_training_batch_report


class DistributedMultiAgentHOODIETrainingBatchReportTests(unittest.TestCase):
    def test_artifacts_written(self) -> None:
        build_distributed_multi_agent_hoodie_training_batch_report()
        path = Path("artifacts/analysis/distributed-multi-agent-hoodie-training-batch/distributed-multi-agent-hoodie-training-batch-report.json")
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["feature_id"], "066-distributed-multi-agent-hoodie-training-batch")


if __name__ == "__main__":
    unittest.main()

