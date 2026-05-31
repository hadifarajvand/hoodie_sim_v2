from __future__ import annotations

import unittest

from src.analysis.baseline_policy_comparative_evaluation_readiness.report import build_action_bound_outcome
from src.analysis.proposed_method_integration_readiness.model import PROPOSED_METHOD_POLICY_ID
from src.analysis.proposed_method_integration_readiness.report import build_feature_075_report
from src.policies import PolicyContext


class ProposedMethodIntegrationReadinessScoringTests(unittest.TestCase):
    def test_candidate_ranking_and_action_bound_outcomes_vary_by_scenario(self) -> None:
        report = build_feature_075_report()
        evaluations = {evaluation.scenario_id: evaluation for evaluation in report.scenario_evaluations}

        self.assertEqual(evaluations["light_load_no_deadline_pressure"].selected_action_family, "local")
        self.assertEqual(evaluations["legal_horizontal_offload"].selected_action_family, "horizontal")
        self.assertEqual(evaluations["cloud_vertical_fallback"].selected_action_family, "vertical")
        self.assertEqual(evaluations["timeout_drop_case"].selected_action_family, "vertical")
        self.assertEqual(evaluations["timeout_drop_case"].action_bound_terminal_status, "dropped_timeout")

        selected_families = {evaluation.selected_action_family for evaluation in report.scenario_evaluations}
        self.assertGreater(len(selected_families), 1)
        signatures = {
            (
                evaluation.selected_action_family,
                evaluation.action_bound_terminal_status,
                evaluation.metrics.completed_count,
                evaluation.metrics.dropped_timeout_count,
                evaluation.metrics.dropped_unavailable_count,
                evaluation.metrics.average_delay,
                evaluation.metrics.average_reward,
            )
            for evaluation in report.scenario_evaluations
        }
        self.assertGreater(len(signatures), 2)
        self.assertTrue(all(evaluation.candidate_ranking_trace_present for evaluation in report.scenario_evaluations))
        self.assertTrue(all(evaluation.deadline_slack_evidence_present for evaluation in report.scenario_evaluations))
        self.assertTrue(all(evaluation.queue_or_load_evidence_present for evaluation in report.scenario_evaluations))
        self.assertTrue(all(evaluation.topology_legality_enforced for evaluation in report.scenario_evaluations))
        self.assertTrue(all(evaluation.action_bound_metrics_derived for evaluation in report.scenario_evaluations))
        self.assertTrue(all(not evaluation.compatibility_mode_used for evaluation in report.scenario_evaluations))

    def test_horizontal_selected_actions_use_feature_070_topology_and_illegal_destinations_fail(self) -> None:
        context = PolicyContext(
            observation={
                "scenario_id": "legal_horizontal_offload",
                "source_agent_id": "1",
                "horizontal_destinations": ("6", "2"),
                "local_action": "local",
                "cloud_action": "cloud",
            },
            legal_action_mask={
                "local": True,
                "cloud": True,
                "vertical": True,
                "horizontal": True,
                "offload_horizontal": True,
                "6": True,
                "2": False,
                "1": True,
            },
            trace_history=(PROPOSED_METHOD_POLICY_ID, "legal_horizontal_offload"),
        )
        legal = build_action_bound_outcome(PROPOSED_METHOD_POLICY_ID, "legal_horizontal_offload", "6", context)
        illegal = build_action_bound_outcome(PROPOSED_METHOD_POLICY_ID, "legal_horizontal_offload", "2", context)
        self.assertEqual(legal.selected_action_family, "horizontal")
        self.assertEqual(legal.action_legality, "legal")
        self.assertEqual(legal.terminal_status, "completed_public")
        self.assertEqual(illegal.action_legality, "illegal_unavailable")
        self.assertEqual(illegal.terminal_status, "dropped_unavailable")
        self.assertEqual(illegal.metrics.dropped_unavailable_count, 1)
        self.assertEqual(illegal.metrics.illegal_action_rejection_count, 1)

        self_refusal = build_action_bound_outcome(PROPOSED_METHOD_POLICY_ID, "legal_horizontal_offload", "1", context)
        self.assertEqual(self_refusal.action_legality, "illegal_self_destination")
        self.assertEqual(self_refusal.terminal_status, "dropped_unavailable")

    def test_terminal_status_cannot_override_topology_legality(self) -> None:
        context = PolicyContext(
            observation={
                "scenario_id": "illegal_horizontal_destination_attempt",
                "source_agent_id": "1",
                "horizontal_destinations": ("6", "2"),
                "local_action": "local",
                "cloud_action": "cloud",
            },
            legal_action_mask={
                "local": True,
                "cloud": True,
                "vertical": True,
                "horizontal": True,
                "offload_horizontal": True,
                "6": True,
                "2": False,
                "1": True,
            },
            trace_history=(PROPOSED_METHOD_POLICY_ID, "illegal_horizontal_destination_attempt"),
        )
        illegal = build_action_bound_outcome(PROPOSED_METHOD_POLICY_ID, "illegal_horizontal_destination_attempt", "2", context)
        self.assertEqual(illegal.action_legality, "illegal_unavailable")
        self.assertEqual(illegal.terminal_status, "dropped_unavailable")
        self.assertEqual(illegal.metrics.illegal_action_rejection_count, 1)


if __name__ == "__main__":
    unittest.main()
