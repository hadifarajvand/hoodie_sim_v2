from __future__ import annotations

import unittest

from src.analysis.paper_faithful_state_action_space_batch import build_paper_faithful_state_action_space_batch_report


class PaperFaithfulStateActionSpaceBatchMetricsTests(unittest.TestCase):
    def test_paper_state_is_not_legacy_three_dimensional(self) -> None:
        payload = build_paper_faithful_state_action_space_batch_report().to_dict()
        self.assertTrue(payload["paper_state_contract_summary"]["paper_state_not_legacy_three_dimensional"])
        self.assertTrue(payload["waiting_time_summary"]["waiting_times_explicit"])
        self.assertTrue(payload["public_queue_vector_summary"]["public_queue_vector_not_scalar"])

    def test_action_space_and_legal_mask_are_destination_specific(self) -> None:
        payload = build_paper_faithful_state_action_space_batch_report().to_dict()
        self.assertTrue(payload["destination_action_space_summary"]["destination_action_space_enabled"])
        self.assertTrue(payload["legal_mask_summary"]["legal_mask_destination_specific"])
        self.assertGreaterEqual(payload["destination_action_space_summary"]["paper_action_count"], 22)


if __name__ == "__main__":
    unittest.main()
