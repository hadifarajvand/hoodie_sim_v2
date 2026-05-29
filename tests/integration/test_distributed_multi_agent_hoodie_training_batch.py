from __future__ import annotations

import unittest

from src.analysis.distributed_multi_agent_hoodie_training_batch import build_distributed_multi_agent_hoodie_training_batch_report


class DistributedMultiAgentHOODIETrainingBatchIntegrationTests(unittest.TestCase):
    def test_report_passes(self) -> None:
        payload = build_distributed_multi_agent_hoodie_training_batch_report().to_dict()
        self.assertEqual(payload["final_verdict"], "distributed_multi_agent_hoodie_training_batch_passed")
        self.assertEqual(payload["remaining_blockers"], [])


if __name__ == "__main__":
    unittest.main()

