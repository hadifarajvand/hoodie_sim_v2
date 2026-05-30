from __future__ import annotations

import unittest

from src.evaluation.policy_registry import PolicyRegistry
from src.policies import PolicyContext
from src.policies.mleo import DelayCandidate, build_delay_candidates


class MinimumLatencyEstimatePolicyTests(unittest.TestCase):
    def context(self, observation: dict[str, object], mask: dict[str, bool] | None = None) -> PolicyContext:
        return PolicyContext(
            observation=observation,
            legal_action_mask=mask or {"local": True, "horizontal": True, "vertical": True},
            trace_history=("mleo",),
        )

    def test_candidate_extraction_includes_local_horizontal_and_vertical_components(self) -> None:
        context = self.context(
            {
                "mleo_delay_candidates": {
                    "local": {"queue_delay": 1.0, "transmission_delay": 0.0, "compute_delay": 4.0},
                    "horizontal": {"queue_delay": 2.0, "transmission_delay": 1.0, "compute_delay": 1.0},
                    "vertical": {"queue_delay": 1.0, "transmission_delay": 3.0, "compute_delay": 2.0},
                }
            }
        )
        candidates = build_delay_candidates(context)
        self.assertEqual([candidate.action_family for candidate in candidates], ["local", "horizontal", "vertical"])
        self.assertEqual([candidate.total_delay for candidate in candidates], [5.0, 4.0, 6.0])
        self.assertTrue(all(isinstance(candidate, DelayCandidate) for candidate in candidates))

    def test_flat_observation_fields_are_extracted(self) -> None:
        context = self.context(
            {
                "local_queue_delay": 1.0,
                "local_transmission_delay": 0.0,
                "local_compute_delay": 2.0,
                "horizontal_total_delay": 1.5,
                "vertical_total_delay": 3.0,
            }
        )
        candidates = build_delay_candidates(context)
        totals = {candidate.action_family: candidate.total_delay for candidate in candidates}
        self.assertEqual(totals["local"], 3.0)
        self.assertEqual(totals["horizontal"], 1.5)
        self.assertEqual(totals["vertical"], 3.0)

    def test_placement_candidates_are_extracted_for_local_cloud_and_edge_placements(self) -> None:
        context = self.context(
            {
                "queue_delay_estimates": {"local": 1.0, "cloud": 4.0, "2": 2.0, "3": 0.5},
                "mleo_placement_candidates": [
                    {"action_id": "local", "action_family": "local", "transmission_delay": 0.0, "compute_delay": 1.0},
                    {"action_id": "cloud", "action_family": "vertical", "transmission_delay": 1.0, "compute_delay": 1.0},
                    {"action_id": "2", "action_family": "horizontal", "transmission_delay": 1.0, "compute_delay": 1.0},
                    {"action_id": "3", "action_family": "horizontal", "transmission_delay": 0.5, "compute_delay": 0.5},
                ],
            },
            {"local": True, "cloud": True, "2": True, "3": True},
        )
        candidates = build_delay_candidates(context)
        self.assertEqual([candidate.action_id for candidate in candidates], ["local", "cloud", "2", "3"])
        totals = {candidate.action_id: candidate.total_delay for candidate in candidates}
        self.assertEqual(totals["local"], 2.0)
        self.assertEqual(totals["cloud"], 6.0)
        self.assertEqual(totals["2"], 4.0)
        self.assertEqual(totals["3"], 1.5)
        self.assertTrue(all(isinstance(candidate, DelayCandidate) for candidate in candidates))

    def test_unavailable_candidates_are_removed_before_ranking(self) -> None:
        policy = PolicyRegistry.resolve("MLEO")
        context = self.context(
            {
                "mleo_delay_candidates": {
                    "local": {"total_delay": 1.0},
                    "horizontal": {"total_delay": 2.0},
                    "vertical": {"total_delay": 3.0},
                }
            },
            {"local": False, "horizontal": True, "vertical": True},
        )
        self.assertEqual(policy.choose_action(context), "horizontal")
        self.assertFalse(next(candidate for candidate in policy.last_candidates if candidate.action_family == "local").available)

    def test_unavailable_placement_candidates_are_removed_before_ranking(self) -> None:
        policy = PolicyRegistry.resolve("MLEO")
        context = self.context(
            {
                "mleo_placement_candidates": [
                    {"action_id": "local", "action_family": "local", "total_delay": 1.0, "available": False},
                    {"action_id": "cloud", "action_family": "vertical", "total_delay": 2.0},
                    {"action_id": "2", "action_family": "horizontal", "total_delay": 3.0},
                ]
            },
            {"local": False, "cloud": True, "2": True},
        )
        self.assertEqual(policy.choose_action(context), "cloud")
        self.assertFalse(next(candidate for candidate in policy.last_candidates if candidate.action_id == "local").available)

    def test_total_delay_ranking_chooses_lowest_comparable_candidate(self) -> None:
        policy = PolicyRegistry.resolve("MLEO")
        context = self.context(
            {
                "mleo_delay_candidates": {
                    "local": {"queue_delay": 2.0, "transmission_delay": 0.0, "compute_delay": 2.0},
                    "horizontal": {"queue_delay": 1.0, "transmission_delay": 1.0, "compute_delay": 1.0},
                    "vertical": {"queue_delay": 4.0, "transmission_delay": 1.0, "compute_delay": 1.0},
                }
            }
        )
        self.assertEqual(policy.choose_action(context), "horizontal")
        self.assertIsNone(policy.last_fallback_reason)

    def test_total_delay_ranking_prefers_lowest_placement_candidate(self) -> None:
        policy = PolicyRegistry.resolve("MLEO")
        context = self.context(
            {
                "queue_delay_estimates": {"local": 1.0, "cloud": 4.0, "2": 0.5},
                "mleo_placement_candidates": [
                    {"action_id": "local", "action_family": "local", "compute_delay": 1.0},
                    {"action_id": "cloud", "action_family": "vertical", "transmission_delay": 1.0, "compute_delay": 1.0},
                    {"action_id": "2", "action_family": "horizontal", "transmission_delay": 0.5, "compute_delay": 0.5},
                ],
            },
            {"local": True, "cloud": True, "2": True},
        )
        self.assertEqual(policy.choose_action(context), "2")
        self.assertIsNone(policy.last_fallback_reason)

    def test_deterministic_tie_handling_prefers_local_then_horizontal_then_vertical(self) -> None:
        policy = PolicyRegistry.resolve("MLEO")
        context = self.context(
            {
                "mleo_delay_candidates": {
                    "local": {"total_delay": 5.0},
                    "horizontal": {"total_delay": 5.0},
                    "vertical": {"total_delay": 5.0},
                }
            }
        )
        self.assertEqual(policy.choose_action(context), "local")
        context_without_local = self.context(
            {
                "mleo_delay_candidates": {
                    "local": {"total_delay": 5.0},
                    "horizontal": {"total_delay": 5.0},
                    "vertical": {"total_delay": 5.0},
                }
            },
            {"local": False, "horizontal": True, "vertical": True},
        )
        self.assertEqual(policy.choose_action(context_without_local), "horizontal")

    def test_placement_tie_handling_prefers_local_then_cloud_then_horizontal(self) -> None:
        policy = PolicyRegistry.resolve("MLEO")
        tied_payload = {
            "mleo_placement_candidates": [
                {"action_id": "local", "action_family": "local", "total_delay": 5.0},
                {"action_id": "cloud", "action_family": "vertical", "total_delay": 5.0},
                {"action_id": "2", "action_family": "horizontal", "total_delay": 5.0},
            ]
        }
        context = self.context(tied_payload, {"local": True, "cloud": True, "2": True})
        self.assertEqual(policy.choose_action(context), "local")
        context_without_local = self.context(tied_payload, {"local": False, "cloud": True, "2": True})
        self.assertEqual(policy.choose_action(context_without_local), "cloud")

    def test_missing_fields_use_visible_fallback_hints(self) -> None:
        policy = PolicyRegistry.resolve("MLEO")
        context = self.context(
            {"fallback_hints": {"local": 3.0, "horizontal": 1.0, "vertical": 2.0}},
            {"local": True, "horizontal": True, "vertical": True},
        )
        self.assertEqual(policy.choose_action(context), "horizontal")
        self.assertEqual(policy.last_fallback_reason, "no available delay candidates have comparable total delay")
        self.assertTrue(all(candidate.total_delay is None for candidate in policy.last_candidates))

    def test_missing_placement_fields_use_visible_fallback_hints(self) -> None:
        policy = PolicyRegistry.resolve("MLEO")
        context = self.context(
            {
                "mleo_placement_candidates": [
                    {"action_id": "local", "action_family": "local"},
                    {"action_id": "cloud", "action_family": "vertical"},
                    {"action_id": "2", "action_family": "horizontal"},
                ],
                "fallback_hints": {"local": 3.0, "cloud": 1.0, "horizontal": 2.0},
            },
            {"local": True, "cloud": True, "2": True},
        )
        self.assertEqual(policy.choose_action(context), "cloud")
        self.assertEqual(policy.last_fallback_reason, "no available delay candidates have comparable total delay")
        self.assertTrue(all(candidate.total_delay is None for candidate in policy.last_candidates))

    def test_missing_fields_without_hints_use_documented_mask_order_fallback(self) -> None:
        policy = PolicyRegistry.resolve("MLEO")
        context = self.context({}, {"local": False, "horizontal": False, "vertical": True})
        self.assertEqual(policy.choose_action(context), "vertical")
        self.assertEqual(policy.last_fallback_reason, "no available delay candidates have comparable total delay")

    def test_latency_estimates_remain_supported_as_candidate_totals(self) -> None:
        policy = PolicyRegistry.resolve("MLEO")
        context = self.context({"latency_estimates": {"local": 9.0, "horizontal": 4.0, "vertical": 5.0}})
        self.assertEqual(policy.choose_action(context), "horizontal")


if __name__ == "__main__":
    unittest.main()
