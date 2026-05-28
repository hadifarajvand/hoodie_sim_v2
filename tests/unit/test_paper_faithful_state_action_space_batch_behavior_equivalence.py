from __future__ import annotations

import unittest

from src.analysis.paper_faithful_state_action_space_batch import build_paper_faithful_state_action_space_batch_report


class PaperFaithfulStateActionSpaceBatchBehaviorEquivalenceTests(unittest.TestCase):
    def test_compatibility_and_migration_flags_are_explicit(self) -> None:
        payload = build_paper_faithful_state_action_space_batch_report().to_dict()
        self.assertTrue(payload["compatibility_summary"]["legacy_training_behavior_preserved"])
        self.assertTrue(payload["compatibility_summary"]["paper_faithful_contract_available"])
        self.assertTrue(payload["compatibility_summary"]["feature_066_required_to_bind_training"])

    def test_behavior_equivalence_check_names_are_unique(self) -> None:
        payload = build_paper_faithful_state_action_space_batch_report().to_dict()
        names = [entry["name"] for entry in payload.get("prerequisite_tags_verified", [])]
        self.assertEqual(len(names), len(set(names)))


if __name__ == "__main__":
    unittest.main()
