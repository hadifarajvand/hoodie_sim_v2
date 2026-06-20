from __future__ import annotations

import unittest

from src.analysis.evaluation_instrumentation_reward_state_diagnostic.runner import _build_state_feature_coverage_audit, _build_state_feature_coverage_result


class EvaluationInstrumentationRewardStateDiagnosticStateCoverageTests(unittest.TestCase):
    def test_state_feature_coverage_audit_has_expected_fields(self) -> None:
        audit = _build_state_feature_coverage_audit()
        result = _build_state_feature_coverage_result(audit)
        field_names = [entry["field_name"] for entry in audit]
        self.assertEqual(len(field_names), 19)
        self.assertIn("slot", field_names)
        self.assertIn("pending_at_horizon", field_names)
        slot_entry = next(entry for entry in audit if entry["field_name"] == "slot")
        deadline_entry = next(entry for entry in audit if entry["field_name"] == "deadline")
        pending_entry = next(entry for entry in audit if entry["field_name"] == "pending_at_horizon")
        self.assertTrue(slot_entry["available_in_environment_observation"])
        self.assertTrue(slot_entry["included_in_policy_state_vector"])
        self.assertFalse(deadline_entry["included_in_policy_state_vector"])
        self.assertTrue(pending_entry["included_in_replay_transition"])
        self.assertIn("high_risk_missing_fields", result)
        self.assertTrue(result["high_risk_missing_fields"])


if __name__ == "__main__":
    unittest.main()
