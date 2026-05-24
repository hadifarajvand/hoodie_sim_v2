from __future__ import annotations

import unittest

from src.analysis.selected_action_outcome_evidence_rerun import build_selected_action_outcome_evidence_rerun_report


class SelectedActionOutcomeEvidenceRerunBehaviorEquivalenceTests(unittest.TestCase):
    def test_behavior_equivalence_checks_unique_and_passed(self) -> None:
        payload = build_selected_action_outcome_evidence_rerun_report().to_dict()
        checks = payload["behavior_equivalence_summary"]["checks"]
        names = [check["name"] for check in checks]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(payload["behavior_equivalence_passed"], payload["behavior_equivalence_summary"]["passed"])
        self.assertTrue(payload["behavior_equivalence_passed"])


if __name__ == "__main__":
    unittest.main()
