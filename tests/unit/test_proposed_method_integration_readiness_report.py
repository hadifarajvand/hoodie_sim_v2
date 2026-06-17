from __future__ import annotations

import unittest

from src.analysis.proposed_method_integration_readiness.model import (
    PROPOSED_METHOD_POLICY_FAMILY,
    PROPOSED_METHOD_POLICY_ID,
)
from src.analysis.proposed_method_integration_readiness.report import build_feature_075_report, render_feature_075_report


class ProposedMethodIntegrationReadinessReportTests(unittest.TestCase):
    def test_feature_075_report_passes_only_when_all_action_bound_gates_pass(self) -> None:
        report = build_feature_075_report()
        self.assertFalse(report.passed)
        self.assertEqual(report.status, "proposed_method_integration_readiness_with_blockers")
        self.assertEqual(report.feature_name, "Feature 075 - Proposed Method Integration Readiness")
        self.assertEqual(report.proposed_method_descriptor.policy_id, PROPOSED_METHOD_POLICY_ID)
        self.assertEqual(report.proposed_method_descriptor.policy_family, PROPOSED_METHOD_POLICY_FAMILY)
        self.assertEqual(len(report.scenario_evaluations), 7)
        self.assertEqual(len(report.policy_aggregate_metrics), 1)
        self.assertTrue(all(evaluation.selected_action_id for evaluation in report.scenario_evaluations))
        self.assertTrue(all(evaluation.selected_action_family for evaluation in report.scenario_evaluations))
        self.assertTrue(all(evaluation.candidate_ranking_trace_present for evaluation in report.scenario_evaluations))
        self.assertTrue(all(evaluation.deadline_slack_evidence_present for evaluation in report.scenario_evaluations))
        self.assertTrue(all(evaluation.queue_or_load_evidence_present for evaluation in report.scenario_evaluations))
        self.assertTrue(all(evaluation.topology_legality_enforced for evaluation in report.scenario_evaluations))
        self.assertTrue(all(evaluation.action_bound_metrics_derived for evaluation in report.scenario_evaluations))
        self.assertTrue(all(not evaluation.compatibility_mode_used for evaluation in report.scenario_evaluations))
        self.assertTrue(all(not aggregate.compatibility_mode_used for aggregate in report.policy_aggregate_metrics))
        self.assertTrue(all(aggregate.action_bound_metrics_derived for aggregate in report.policy_aggregate_metrics))
        self.assertTrue(all(aggregate.topology_legality_enforced for aggregate in report.policy_aggregate_metrics))
        self.assertTrue(all(aggregate.candidate_ranking_trace_present for aggregate in report.policy_aggregate_metrics))

    def test_claim_boundary_and_rendered_report_are_explicit_about_scope_and_no_overclaim(self) -> None:
        report = build_feature_075_report()
        rendered = render_feature_075_report(report)
        boundary = report.paper_claim_boundary.lower()
        self.assertIn("no training claim is made", boundary)
        self.assertIn("no final evaluation claim is made", boundary)
        self.assertIn("no performance superiority claim is made", boundary)
        self.assertIn("no statistical significance claim is made", boundary)
        self.assertIn("no full paper reproduction claim is made", boundary)
        rendered_lower = rendered.lower()
        self.assertNotIn("proposed_dcq", rendered_lower)
        self.assertNotIn("proposed_deadline_queueing", rendered_lower)
        self.assertIn("feature 073 controlled scenarios are used as fixtures, not copied final metrics.", rendered_lower)
        self.assertIn("selected policy actions are bound to controlled outcomes.", rendered_lower)
        self.assertIn("local selected actions map to local/private controlled outcomes.", rendered_lower)
        self.assertIn("vertical/cloud selected actions map to cloud/vertical controlled outcomes.", rendered_lower)
        self.assertIn("horizontal selected actions use feature 070 figure 7 topology.", rendered_lower)
        self.assertIn("feature 071 helpers are used for paper-mode terminal and reward behavior.", rendered_lower)
        self.assertIn("compatibility mode is excluded from the default proposed-method evaluation.", rendered_lower)
        self.assertIn("no training claim is made.", rendered_lower)
        self.assertIn("no final evaluation claim is made.", rendered_lower)
        self.assertIn("no performance superiority claim is made.", rendered_lower)
        self.assertIn("no statistical significance claim is made.", rendered_lower)
        self.assertIn("no full paper reproduction claim is made.", rendered_lower)


if __name__ == "__main__":
    unittest.main()
