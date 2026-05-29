from __future__ import annotations

import unittest

from src.analysis.paper_traffic_queue_communication_fidelity_batch import build_paper_traffic_queue_communication_fidelity_batch_report


class PaperTrafficQueueCommunicationFidelityBatchBehaviorEquivalenceTests(unittest.TestCase):
    def test_compatibility_flags(self) -> None:
        payload = build_paper_traffic_queue_communication_fidelity_batch_report().to_dict()
        self.assertTrue(payload["queue_fidelity_summary"]["feature_065_state_compatibility_preserved"])
        self.assertTrue(payload["pubsub_summary"]["feature_066_distributed_training_compatibility_preserved"])


if __name__ == "__main__":
    unittest.main()

