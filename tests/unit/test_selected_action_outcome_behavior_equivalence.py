from __future__ import annotations

import unittest

from src.analysis.selected_action_family_per_action_outcome_evidence import build_selected_action_outcome_evidence_report


class SelectedActionOutcomeBehaviorEquivalenceTest(unittest.TestCase):
    def test_behavior_equivalence_checks_are_unique(self) -> None:
        payload = build_selected_action_outcome_evidence_report().to_dict()
        checks = payload["behavior_equivalence_summary"]["checks"]
        names = [check["name"] for check in checks]
        self.assertEqual(len(names), len(set(names)))

    def test_behavior_equivalence_pass_through(self) -> None:
        payload = build_selected_action_outcome_evidence_report().to_dict()
        self.assertEqual(payload["behavior_equivalence_passed"], payload["behavior_equivalence_summary"]["passed"])


if __name__ == "__main__":
    unittest.main()
