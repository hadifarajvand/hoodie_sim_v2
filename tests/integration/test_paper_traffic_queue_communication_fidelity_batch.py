from __future__ import annotations

import unittest

from src.analysis.paper_traffic_queue_communication_fidelity_batch import build_paper_traffic_queue_communication_fidelity_batch_report


class PaperTrafficQueueCommunicationFidelityBatchIntegrationTests(unittest.TestCase):
    def test_passes(self) -> None:
        payload = build_paper_traffic_queue_communication_fidelity_batch_report().to_dict()
        self.assertEqual(payload["final_verdict"], "paper_traffic_queue_communication_fidelity_batch_passed")
        self.assertEqual(payload["remaining_blockers"], [])


if __name__ == "__main__":
    unittest.main()

