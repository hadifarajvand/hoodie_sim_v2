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
            "timeout_drop_rule_evidence",
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
        self.assertFalse(payload["passed"])
        self.assertEqual(payload["topology_evidence"]["evidence_status"], "verified_manual_paper_extraction")
        self.assertEqual(len(payload["topology_evidence"]["neighbor_map"]), 20)
        self.assertEqual(payload["topology_evidence"]["neighbor_map"]["1"], ["6", "11", "16"])
        self.assertIn("figure-7-topology-extraction.md", payload["topology_evidence"]["provenance"])
        self.assertEqual(payload["timeout_drop_rule_evidence"]["timeout_relation"], "deadline_slot = arrival_slot + timeout_phi - 1")
        self.assertIn("src/environment/paper_timeout.py", payload["timeout_drop_rule_evidence"]["searched_sources"])
        self.assertEqual(payload["neighbor_legality_evidence"]["final_legal"], True)
        self.assertEqual(payload["neighbor_legality_evidence"]["destination_agent_id"], "6")
        self.assertEqual(payload["timeout_drop_accounting_evidence"]["paper_semantics_status"], "blocked_by_unresolved_terminal_grace_behavior")
        self.assertEqual(payload["timeout_drop_accounting_evidence"]["rule_evidence"]["paper_semantics_status"], "source_backed_rule_with_unresolved_terminal_grace_behavior")
        self.assertEqual(payload["reward_equation_evidence"]["recovered_status"], "source_backed_partial")
        self.assertIn("reward_evidence.md", payload["reward_equation_evidence"]["provenance"])
        self.assertEqual(payload["terminal_reward_evidence"]["timing_valid"], False)
        self.assertEqual(len(payload["blockers"]), 2)
        self.assertEqual({blocker["category"] for blocker in payload["blockers"]}, {"timeout_drop", "reward"})
        self.assertTrue(payload["feature_068r_regression_status"]["passed"])
        self.assertTrue(payload["feature_069_regression_status"]["passed"])
        self.assertIn("No full paper reproduction claim", payload["paper_claim_boundary"])

    def test_report_rejects_passing_with_invalid_terminal_reward_timing(self) -> None:
        with self.assertRaises(ValueError):
            from src.analysis.topology_timeout_reward_fidelity.report import (
                _feature_068r_regression_evidence,
                _feature_069_regression_evidence,
                _neighbor_legality_evidence,
                _reward_equation_evidence,
                _terminal_reward_evidence,
                _timeout_drop_accounting_evidence,
                _timeout_drop_rule_evidence,
                _topology_evidence,
            )

            from src.analysis.topology_timeout_reward_fidelity.model import Feature070FidelityReport

            Feature070FidelityReport(
                feature_name="Feature 070 - Topology, Timeout/Drop, and Reward Fidelity",
                status="mechanism_fidelity_readiness_with_blockers",
                passed=True,
                changed_files=("specs/070-topology-timeout-reward-fidelity/tasks.md",),
                topology_evidence=_topology_evidence(),
                neighbor_legality_evidence=_neighbor_legality_evidence(),
                timeout_drop_rule_evidence=_timeout_drop_rule_evidence(),
                timeout_drop_accounting_evidence=_timeout_drop_accounting_evidence(),
                reward_equation_evidence=_reward_equation_evidence(),
                terminal_reward_evidence=_terminal_reward_evidence(),
                blockers=(),
                feature_068r_regression_status=_feature_068r_regression_evidence(),
                feature_069_regression_status=_feature_069_regression_evidence(),
                paper_claim_boundary="boundary",
                recommended_next_feature="next",
            )

    def test_report_rejects_passing_when_reward_slot_precedes_terminal_slot(self) -> None:
        from src.analysis.topology_timeout_reward_fidelity.model import Feature070FidelityReport, TerminalRewardEvidence
        from src.analysis.topology_timeout_reward_fidelity.report import (
            _feature_068r_regression_evidence,
            _feature_069_regression_evidence,
            _neighbor_legality_evidence,
            _reward_equation_evidence,
            _timeout_drop_accounting_evidence,
            _timeout_drop_rule_evidence,
            _topology_evidence,
        )

        with self.assertRaises(ValueError) as ctx:
            Feature070FidelityReport(
                feature_name="Feature 070 - Topology, Timeout/Drop, and Reward Fidelity",
                status="mechanism_fidelity_readiness_with_blockers",
                passed=True,
                changed_files=("specs/070-topology-timeout-reward-fidelity/tasks.md",),
                topology_evidence=_topology_evidence(),
                neighbor_legality_evidence=_neighbor_legality_evidence(),
                timeout_drop_rule_evidence=_timeout_drop_rule_evidence(),
                timeout_drop_accounting_evidence=_timeout_drop_accounting_evidence(),
                reward_equation_evidence=_reward_equation_evidence(),
                terminal_reward_evidence=TerminalRewardEvidence(
                    task_id="task-070-1",
                    selected_action="A2",
                    terminal_status="completed",
                    terminal_slot=5,
                    reward_slot=4,
                    reward_value=1.0,
                    reward_equation_id="reward-eq-1",
                    timing_valid=True,
                ),
                blockers=(),
                feature_068r_regression_status=_feature_068r_regression_evidence(),
                feature_069_regression_status=_feature_069_regression_evidence(),
                paper_claim_boundary="boundary",
                recommended_next_feature="next",
            )

        self.assertIn("reward_slot", str(ctx.exception))

    def test_report_preserves_claim_boundary_and_blocker_categories(self) -> None:
        report = build_feature_070_report()
        categories = {blocker.category for blocker in report.blockers}
        self.assertEqual(categories, {"timeout_drop", "reward"})
        self.assertIn("structured evidence", report.paper_claim_boundary)
        self.assertIn("Feature 068R", report.feature_068r_regression_status.summary)
        self.assertIn("Feature 069", report.feature_069_regression_status.summary)
        self.assertEqual(report.timeout_drop_rule_evidence.paper_semantics_status, "source_backed_rule_with_unresolved_terminal_grace_behavior")
        self.assertIn("reward_evidence.md", report.reward_equation_evidence.provenance)


if __name__ == "__main__":
    unittest.main()
