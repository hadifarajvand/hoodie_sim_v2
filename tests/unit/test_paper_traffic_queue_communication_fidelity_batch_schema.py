from __future__ import annotations

import unittest

from src.analysis.paper_traffic_queue_communication_fidelity_batch import build_paper_traffic_queue_communication_fidelity_batch_report


class PaperTrafficQueueCommunicationFidelityBatchSchemaTests(unittest.TestCase):
    def test_report_schema(self) -> None:
        payload = build_paper_traffic_queue_communication_fidelity_batch_report().to_dict()
        self.assertEqual(payload["final_verdict"], "paper_traffic_queue_communication_fidelity_batch_passed")
        self.assertEqual(payload["remaining_blockers"], [])
        self.assertTrue(payload["feature_066_verified"])


if __name__ == "__main__":
    unittest.main()

