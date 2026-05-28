from __future__ import annotations

import unittest

from src.analysis.paper_faithful_state_action_space_batch import build_paper_faithful_state_action_space_batch_report
from src.analysis.paper_faithful_state_action_space_batch.config import FEATURE_ID, REQUIRED_TOP_LEVEL_FIELDS
from src.analysis.paper_faithful_state_action_space_batch.model import PaperFaithfulStateActionSpaceBatchReport


class PaperFaithfulStateActionSpaceBatchSchemaTests(unittest.TestCase):
    def test_report_has_required_fields_and_pass_verdict(self) -> None:
        payload = build_paper_faithful_state_action_space_batch_report().to_dict()
        for key in REQUIRED_TOP_LEVEL_FIELDS:
            self.assertIn(key, payload)
        self.assertEqual(payload["feature_id"], FEATURE_ID)
        self.assertEqual(payload["final_verdict"], "paper_faithful_state_action_space_batch_passed")
        self.assertEqual(payload["remaining_blockers"], [])

    def test_pass_with_blockers_is_rejected(self) -> None:
        payload = build_paper_faithful_state_action_space_batch_report().to_dict()
        payload["remaining_blockers"] = ["feature_064_prerequisite_blocked"]
        payload["final_verdict"] = "paper_faithful_state_action_space_batch_passed"
        with self.assertRaises(ValueError):
            PaperFaithfulStateActionSpaceBatchReport(**payload)


if __name__ == "__main__":
    unittest.main()
