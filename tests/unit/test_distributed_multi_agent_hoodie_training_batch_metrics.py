from __future__ import annotations

import unittest

from src.analysis.distributed_multi_agent_hoodie_training_batch import build_distributed_multi_agent_hoodie_training_batch_report


class DistributedMultiAgentHOODIETrainingBatchMetricsTests(unittest.TestCase):
    def test_per_agent_counts(self) -> None:
        payload = build_distributed_multi_agent_hoodie_training_batch_report().to_dict()
        self.assertEqual(payload["per_agent_model_summary"]["agent_count"], 20)
        self.assertEqual(payload["per_agent_replay_summary"]["per_agent_replay_memory_created"], True)
        self.assertEqual(payload["per_agent_optimizer_summary"]["optimizer_count"], 20)
        self.assertEqual(payload["per_agent_target_network_summary"]["target_network_count"], 20)


if __name__ == "__main__":
    unittest.main()

