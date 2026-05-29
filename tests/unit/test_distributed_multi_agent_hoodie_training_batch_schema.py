from __future__ import annotations

import json
import unittest
from pathlib import Path

from src.analysis.distributed_multi_agent_hoodie_training_batch import build_distributed_multi_agent_hoodie_training_batch_report


class DistributedMultiAgentHOODIETrainingBatchSchemaTests(unittest.TestCase):
    def test_report_schema(self) -> None:
        report = build_distributed_multi_agent_hoodie_training_batch_report()
        payload = report.to_dict()
        self.assertEqual(payload["final_verdict"], "distributed_multi_agent_hoodie_training_batch_passed")
        self.assertEqual(payload["remaining_blockers"], [])
        self.assertEqual(payload["feature_065_verified"], True)
        self.assertTrue(payload["per_agent_model_summary"]["per_agent_ddqn_models_created"])


if __name__ == "__main__":
    unittest.main()

