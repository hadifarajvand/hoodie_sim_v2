from __future__ import annotations

import unittest
from unittest import mock

from src.analysis.paper_traffic_queue_communication_fidelity_batch import build_paper_traffic_queue_communication_fidelity_batch_report


class PaperTrafficQueueCommunicationFidelityBatchScopeGuardTests(unittest.TestCase):
    def test_blocks_forbidden_dirty_paths(self) -> None:
        import src.analysis.paper_traffic_queue_communication_fidelity_batch.runner as runner

        with mock.patch.object(runner, "_feature_066_verified", return_value=False):
            payload = build_paper_traffic_queue_communication_fidelity_batch_report().to_dict()
        self.assertIn("feature_066_prerequisite_blocked", payload["remaining_blockers"])
        self.assertNotEqual(payload["final_verdict"], "paper_traffic_queue_communication_fidelity_batch_passed")


if __name__ == "__main__":
    unittest.main()

