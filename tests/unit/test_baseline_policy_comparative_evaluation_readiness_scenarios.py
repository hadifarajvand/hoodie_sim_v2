from __future__ import annotations

import unittest

from src.analysis.baseline_policy_comparative_evaluation_readiness.report import (
    build_feature_074_report,
    build_policy_scenario_comparisons,
    build_required_policy_descriptors,
)


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

    def test_policy_comparisons_cover_each_policy_and_scenario_with_distinct_trace_provenance(self) -> None:
        comparisons = build_policy_scenario_comparisons()
        self.assertEqual(len(comparisons), 42)
        self.assertTrue(all(comparison.policy_decision_trace_present for comparison in comparisons if comparison.passed))
        self.assertTrue(all(not comparison.compatibility_mode_used for comparison in comparisons))
        ho_legal = next(
            comparison
            for comparison in comparisons
            if comparison.policy_id == "HO" and comparison.scenario_id == "legal_horizontal_offload"
        )
        self.assertTrue(ho_legal.decision_trace)
        self.assertEqual(ho_legal.policy_action_family, "horizontal-offload family")
        self.assertTrue(ho_legal.passed)

    def test_policy_descriptors_expose_required_policies(self) -> None:
        descriptors = build_required_policy_descriptors()
        self.assertEqual({descriptor.policy_id for descriptor in descriptors}, {"FLC", "VO", "HO", "RO", "BCO", "MLEO"})
        self.assertTrue(all(descriptor.available for descriptor in descriptors))
        self.assertTrue(all(descriptor.decision_trace_supported for descriptor in descriptors))


if __name__ == "__main__":
    unittest.main()
