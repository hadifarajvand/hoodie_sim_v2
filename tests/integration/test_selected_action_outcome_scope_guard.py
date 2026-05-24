from __future__ import annotations

import unittest

from src.analysis.selected_action_family_per_action_outcome_evidence import build_selected_action_outcome_evidence_report


class SelectedActionOutcomeScopeGuardIntegrationTest(unittest.TestCase):
    def test_blockers_are_present_when_rerun_is_blocked(self) -> None:
        payload = build_selected_action_outcome_evidence_report().to_dict()
        if not payload["feature_049_can_be_rerun"]:
            self.assertTrue(payload["feature_049_remaining_blockers"])

    def test_final_verdict_does_not_claim_readiness_when_blocked(self) -> None:
        payload = build_selected_action_outcome_evidence_report().to_dict()
        if not payload["feature_049_can_be_rerun"]:
            self.assertNotEqual(payload["final_verdict"], "selected_action_outcome_evidence_ready_for_feature_049_rerun")


if __name__ == "__main__":
    unittest.main()
