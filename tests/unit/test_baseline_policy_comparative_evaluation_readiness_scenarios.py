from __future__ import annotations

import unittest

from src.analysis.baseline_policy_comparative_evaluation_readiness.report import (
    _scenario_context,
    build_action_bound_outcome,
    build_feature_074_report,
    build_policy_scenario_comparisons,
    build_required_policy_descriptors,
)
from src.evaluation.policy_registry import PolicyRegistry


class BaselinePolicyComparativeEvaluationReadinessScenarioTests(unittest.TestCase):
    def test_required_scenarios_are_covered_for_every_required_policy(self) -> None:
        report = build_feature_074_report()
        scenario_ids = {comparison.scenario_id for comparison in report.scenario_comparisons}
        self.assertEqual(
            scenario_ids,
            {
                "light_load_no_deadline_pressure",
                "tight_deadline_pressure",
                "legal_horizontal_offload",
                "illegal_horizontal_destination_attempt",
                "cloud_vertical_fallback",
                "timeout_drop_case",
                "mixed_local_horizontal_cloud_candidates",
            },
        )
        policy_ids = {comparison.policy_id for comparison in report.scenario_comparisons}
        self.assertEqual(policy_ids, {"FLC", "VO", "HO", "RO", "BCO", "MLEO"})
        self.assertEqual(len(report.scenario_comparisons), 42)
        self.assertTrue(all(comparison.action_bound_metrics_derived for comparison in report.scenario_comparisons))
        self.assertTrue(all(not comparison.compatibility_mode_used for comparison in report.scenario_comparisons))

    def test_policy_comparisons_record_selected_action_evidence(self) -> None:
        comparisons = build_policy_scenario_comparisons()
        self.assertEqual(len(comparisons), 42)
        self.assertTrue(all(comparison.policy_decision_trace_present for comparison in comparisons))
        self.assertTrue(all(comparison.selected_action_id for comparison in comparisons))
        self.assertTrue(all(comparison.selected_action_family for comparison in comparisons))
        self.assertTrue(all(comparison.action_bound_metrics_derived for comparison in comparisons))
        ho_legal = next(
            comparison
            for comparison in comparisons
            if comparison.policy_id == "HO" and comparison.scenario_id == "legal_horizontal_offload"
        )
        self.assertTrue(ho_legal.decision_trace)
        self.assertEqual(ho_legal.policy_action_family, "horizontal-offload family")
        self.assertEqual(ho_legal.selected_action_family, "horizontal")
        self.assertEqual(ho_legal.action_legality, "legal")
        self.assertTrue(ho_legal.passed)

    def test_policy_descriptors_expose_required_policies(self) -> None:
        descriptors = build_required_policy_descriptors()
        self.assertEqual({descriptor.policy_id for descriptor in descriptors}, {"FLC", "VO", "HO", "RO", "BCO", "MLEO"})
        self.assertTrue(all(descriptor.available for descriptor in descriptors))
        self.assertTrue(all(descriptor.decision_trace_supported for descriptor in descriptors))

    def test_horizontal_selected_actions_use_figure_7_topology(self) -> None:
        policy = PolicyRegistry.resolve("HO")
        context = _scenario_context("HO", "illegal_horizontal_destination_attempt")

        legal_outcome = build_action_bound_outcome("HO", "illegal_horizontal_destination_attempt", policy.choose_action(context), context)
        illegal_outcome = build_action_bound_outcome("HO", "illegal_horizontal_destination_attempt", "2", context)
        self.assertEqual(legal_outcome.selected_action_family, "horizontal")
        self.assertEqual(legal_outcome.action_legality, "legal")
        self.assertEqual(legal_outcome.terminal_status, "completed_public")
        self.assertEqual(illegal_outcome.action_legality, "illegal_unavailable")
        self.assertEqual(illegal_outcome.terminal_status, "dropped_unavailable")
        self.assertEqual(illegal_outcome.metrics.dropped_unavailable_count, 1)
        self.assertEqual(illegal_outcome.metrics.illegal_action_rejection_count, 1)

    def test_missing_or_unmapped_selected_actions_fail_readiness(self) -> None:
        context = _scenario_context("FLC", "light_load_no_deadline_pressure")
        outcome = build_action_bound_outcome("FLC", "light_load_no_deadline_pressure", "", context)
        self.assertEqual(outcome.action_legality, "unmapped")
        self.assertFalse(outcome.metrics.completed_count)
        self.assertFalse(outcome.metrics.compatibility_mode_used)


if __name__ == "__main__":
    unittest.main()
