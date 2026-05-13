from __future__ import annotations

import unittest

from src.analysis.deadline_timeout_off_by_one_audit import build_deadline_timeout_off_by_one_audit_report


class DeadlineTimeoutOffByOneScopeGuardTests(unittest.TestCase):
    def test_scope_guard_no_training_policy_dependency_campaign_drift(self) -> None:
        report = build_deadline_timeout_off_by_one_audit_report()

        self.assertTrue(report.no_training_or_policy_drift)
        self.assertTrue(report.no_dependency_drift)
        self.assertTrue(report.no_campaign_rerun)


if __name__ == "__main__":
    unittest.main()
