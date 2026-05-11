from __future__ import annotations

import unittest

from src.analysis.computation_delay_cpu_unit_validation.slot_duration import audit_slot_duration_contract


class ComputationDelaySlotDurationMismatchTests(unittest.TestCase):
    def test_mismatch_is_detected_when_feature_027_report_uses_runtime_proxy_value(self) -> None:
        audit = audit_slot_duration_contract(0.1, 0.1, 1.0)
        self.assertEqual(audit.mismatch_status, "repaired")
        self.assertEqual(audit.required_action, "regenerate_feature_027_report")

    def test_repaired_state_is_reported_when_runtime_and_feature_027_match_paper(self) -> None:
        audit = audit_slot_duration_contract(0.1, 0.1, 0.1)
        self.assertEqual(audit.mismatch_status, "matched")
        self.assertEqual(audit.required_action, "none")


if __name__ == "__main__":
    unittest.main()
