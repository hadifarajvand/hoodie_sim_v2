from __future__ import annotations

import unittest

from src.analysis.topology_timeout_reward_fidelity.report import build_feature_070_report


class TopologyTimeoutRewardFidelityReportTests(unittest.TestCase):
    def test_report_schema_contains_separate_track_fields(self) -> None:
        report = build_feature_070_report(
            changed_files=(
                "specs/070-topology-timeout-reward-fidelity/tasks.md",
                "src/analysis/topology_timeout_reward_fidelity/report.py",
                "tests/unit/test_topology_timeout_reward_fidelity_report.py",
            )
        )
        payload = report.to_dict()
        required = {
            "feature_name",
            "status",
            "passed",
            "changed_files",
            "topology_evidence",
            "neighbor_legality_evidence",
            "timeout_drop_accounting_evidence",
            "reward_equation_evidence",
            "terminal_reward_evidence",
            "blockers",
            "feature_068r_regression_status",
            "feature_069_regression_status",
            "paper_claim_boundary",
            "recommended_next_feature",
        }
        self.assertTrue(required.issubset(payload))
        self.assertEqual(payload["feature_name"], "Feature 070 - Topology, Timeout/Drop, and Reward Fidelity")
        self.assertTrue(payload["passed"])
        self.assertEqual(payload["topology_evidence"]["evidence_status"], "blocked")
        self.assertEqual(payload["neighbor_legality_evidence"]["final_legal"], False)
        self.assertEqual(payload["timeout_drop_accounting_evidence"]["paper_semantics_status"], "blocked")
        self.assertEqual(payload["reward_equation_evidence"]["recovered_status"], "blocked")
        self.assertEqual(payload["terminal_reward_evidence"]["timing_valid"], False)
        self.assertEqual(len(payload["blockers"]), 3)
        self.assertTrue(payload["feature_068r_regression_status"]["passed"])
        self.assertTrue(payload["feature_069_regression_status"]["passed"])
        self.assertIn("No full paper reproduction claim", payload["paper_claim_boundary"])

    def test_report_preserves_claim_boundary_and_blocker_categories(self) -> None:
        report = build_feature_070_report()
        categories = {blocker.category for blocker in report.blockers}
        self.assertEqual(categories, {"topology", "timeout_drop", "reward"})
        self.assertIn("structured evidence", report.paper_claim_boundary)
        self.assertIn("Feature 068R", report.feature_068r_regression_status.summary)
        self.assertIn("Feature 069", report.feature_069_regression_status.summary)


if __name__ == "__main__":
    unittest.main()
