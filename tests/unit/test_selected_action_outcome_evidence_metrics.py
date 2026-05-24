from __future__ import annotations

import unittest

from src.analysis.selected_action_family_per_action_outcome_evidence import build_selected_action_outcome_evidence_report


class SelectedActionOutcomeEvidenceMetricsTest(unittest.TestCase):
    def test_selected_action_count_sums_are_not_faked(self) -> None:
        payload = build_selected_action_outcome_evidence_report().to_dict()
        summary = payload["selected_action_family_evidence_summary"]
        if summary["selected_action_count"] is not None:
            self.assertEqual(
                summary["selected_action_count"],
                sum(value or 0 for value in [
                    summary["selected_local_count"],
                    summary["selected_horizontal_count"],
                    summary["selected_vertical_count"],
                ]),
            )

    def test_blocked_report_uses_explicit_unavailability(self) -> None:
        payload = build_selected_action_outcome_evidence_report().to_dict()
        self.assertEqual(payload["selected_action_family_evidence_status"], "unavailable")
        self.assertEqual(payload["selected_action_to_task_join_status"], "unavailable")
        self.assertEqual(payload["per_action_outcome_evidence_status"], "unavailable")
        self.assertFalse(payload["feature_049_can_be_rerun"])
        self.assertTrue(payload["feature_049_remaining_blockers"])


if __name__ == "__main__":
    unittest.main()
