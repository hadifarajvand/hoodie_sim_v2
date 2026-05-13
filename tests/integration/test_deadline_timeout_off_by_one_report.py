from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.deadline_timeout_off_by_one_audit import build_deadline_timeout_off_by_one_audit_report, write_deadline_timeout_off_by_one_audit_report


class DeadlineTimeoutOffByOneReportIntegrationTests(unittest.TestCase):
    def test_report_schema_and_contents(self) -> None:
        report = build_deadline_timeout_off_by_one_audit_report()

        self.assertEqual(report.feature_id, "036-deadline-timeout-off-by-one-audit")
        self.assertEqual(report.timeout_slots, 20)
        self.assertEqual(report.slot_duration_seconds, 0.1)
        self.assertEqual(report.timeout_seconds, 2.0)
        self.assertTrue(report.contradiction_detected)
        self.assertTrue(report.no_paper_recovery_claims)
        self.assertTrue(report.no_dependency_drift)
        self.assertTrue(report.no_training_or_policy_drift)
        self.assertTrue(report.no_reward_timing_change)
        self.assertTrue(report.no_execution_time_contract_drift)
        self.assertTrue(report.no_transmission_delay_contract_drift)
        self.assertTrue(report.no_capacity_sharing_contract_drift)
        self.assertTrue(report.no_campaign_rerun)
        self.assertIn("src/environment/deadline_rules.py", report.repaired_runtime_components)
        self.assertIn("current_slot == absolute_deadline_slot -> not expired", report.boundary_cases_validated)
        self.assertIn("tests.unit.test_deadline_rules", report.tests_run)

    def test_report_writes_json_and_markdown(self) -> None:
        report = build_deadline_timeout_off_by_one_audit_report()

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path, md_path = write_deadline_timeout_off_by_one_audit_report(report, Path(tmpdir) / "artifacts/analysis/deadline-timeout-off-by-one-audit")
            payload = json.loads(json_path.read_text(encoding="utf-8"))

            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())
            self.assertEqual(payload["feature_id"], "036-deadline-timeout-off-by-one-audit")
            self.assertTrue(payload["contradiction_detected"])
            self.assertEqual(payload["final_verdict"], "deadline_timeout_boundary_repaired")


if __name__ == "__main__":
    unittest.main()

