from __future__ import annotations

import unittest

from src.analysis.paper_traffic_queue_communication_fidelity_batch import build_paper_traffic_queue_communication_fidelity_batch_report


class PaperTrafficQueueCommunicationFidelityBatchMetricsTests(unittest.TestCase):
    def test_summary_flags(self) -> None:
        payload = build_paper_traffic_queue_communication_fidelity_batch_report().to_dict()
        self.assertTrue(payload["traffic_model_summary"]["bernoulli_arrivals_available"])
        self.assertTrue(payload["task_processing_summary"]["task_size_set_available"])
        self.assertTrue(payload["timeout_summary"]["timeout_phi_minus_one_semantics"])
        self.assertTrue(payload["link_delay_summary"]["per_link_delay_contract_available"])
        self.assertTrue(payload["queue_fidelity_summary"]["queue_fidelity_contract_available"])
        self.assertTrue(payload["pubsub_summary"]["pubsub_controller_available"])
        self.assertTrue(payload["recovery_summary"]["delayed_message_recovery_available"])


if __name__ == "__main__":
    unittest.main()

