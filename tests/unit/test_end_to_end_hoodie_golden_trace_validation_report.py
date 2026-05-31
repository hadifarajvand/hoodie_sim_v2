from __future__ import annotations

import unittest

from src.analysis.end_to_end_hoodie_golden_trace_validation.report import build_feature_072_report


class EndToEndHoodieGoldenTraceValidationReportTests(unittest.TestCase):
    def test_report_contains_all_required_evidence_and_passes(self) -> None:
        report = build_feature_072_report()
        payload = report.to_dict()
        self.assertEqual(payload["feature_name"], "Feature 072 - End-to-End HOODIE Golden Trace Validation")
        self.assertEqual(payload["status"], "end_to_end_golden_trace_validation_ready")
        self.assertTrue(payload["passed"])
        self.assertEqual(len(payload["scenarios"]), 11)
        self.assertTrue(all(scenario.expected_outputs is not scenario.actual_outputs for scenario in report.scenarios))
        self.assertTrue(payload["feature_068r_regression_status"]["passed"])
        self.assertTrue(payload["feature_069_regression_status"]["passed"])
        self.assertTrue(payload["feature_070_regression_status"]["passed"])
        self.assertTrue(payload["feature_071_regression_status"]["passed"])
        self.assertIn("No full paper reproduction claim", payload["paper_claim_boundary"])
        self.assertIn("deterministic end-to-end semantic traces", payload["paper_claim_boundary"])
        self.assertIn("Expected outputs are independent scenario constants", payload["paper_claim_boundary"])
        self.assertIn("actual outputs are computed from Feature 070 topology evidence and Feature 071 helpers", payload["paper_claim_boundary"])
        self.assertIn("Feature 073", payload["recommended_next_feature"])
        self.assertIn("src.environment.paper_timeout.is_success_before_deadline", payload["scenarios"][0]["steps"][3]["evidence_source"])
        self.assertEqual(payload["scenarios"][2]["steps"][2]["evidence_source"], "specs/070-topology-timeout-reward-fidelity/evidence/figure-7-topology-extraction.md")
        self.assertEqual(payload["scenarios"][0]["actual_outputs"]["action_selection"]["action_type"], "local")
        self.assertFalse(payload["scenarios"][0]["actual_outputs"]["topology"]["topology_check_required"])
        self.assertEqual(payload["scenarios"][2]["actual_outputs"]["topology"]["destination_agent_id"], "6")
        self.assertTrue(payload["scenarios"][2]["actual_outputs"]["topology"]["topology_check_required"])

    def test_report_rejects_full_paper_claim_and_keeps_ready_status(self) -> None:
        report = build_feature_072_report()
        self.assertNotIn("full paper reproduction is claimed", report.paper_claim_boundary)
        self.assertEqual(report.status, "end_to_end_golden_trace_validation_ready")


if __name__ == "__main__":
    unittest.main()
