from __future__ import annotations

import unittest

from src.evaluation.policy_registry import PolicyRegistry
from src.policies import PolicyContext
from src.policies.bco import BalancedCooperationOffloadingPolicy
from src.policies.common import action_family
from src.policies.flc import FullLocalComputingPolicy
from src.policies.ho import HorizontalOffloadingPolicy
from src.policies.mleo import (
    DelayCandidate,
    MinimumLatencyEstimateOffloadingPolicy,
    build_delay_candidates,
)
from src.policies.ro import RandomOffloadingPolicy
from src.policies.vo import VerticalOffloadingPolicy


class Phase0ValidationGate1RegistryCoverage(unittest.TestCase):
    def test_gate1_all_required_paper_baselines_are_registered(self) -> None:
        expected_types = {
            "FLC": FullLocalComputingPolicy,
            "VO": VerticalOffloadingPolicy,
            "HO": HorizontalOffloadingPolicy,
            "RO": RandomOffloadingPolicy,
            "BCO": BalancedCooperationOffloadingPolicy,
            "MLEO": MinimumLatencyEstimateOffloadingPolicy,
        }
        for name, expected_type in expected_types.items():
            with self.subTest(name=name):
                self.assertIsInstance(PolicyRegistry.resolve(name), expected_type)
        self.assertIn("ADAPTIVE", PolicyRegistry.supported_names())

    def test_gate1_aliases_are_preserved(self) -> None:
        self.assertIsInstance(PolicyRegistry.resolve("full-local-computing"), FullLocalComputingPolicy)
        self.assertIsInstance(PolicyRegistry.resolve("vertical_offloading"), VerticalOffloadingPolicy)
        self.assertIsInstance(PolicyRegistry.resolve("horizontal_offloading"), HorizontalOffloadingPolicy)
        self.assertIsInstance(PolicyRegistry.resolve("random_offloading"), RandomOffloadingPolicy)
        self.assertIsInstance(PolicyRegistry.resolve("balanced_cooperation_offloading"), BalancedCooperationOffloadingPolicy)
        self.assertIsInstance(PolicyRegistry.resolve("minimum_latency_estimate_offloading"), MinimumLatencyEstimateOffloadingPolicy)

    def test_gate1_unsupported_policy_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            PolicyRegistry.resolve("UNKNOWN")


class Phase0ValidationGate2ActionMaskCompliance(unittest.TestCase):
    def test_gate2_every_baseline_returns_only_legal_actions(self) -> None:
        cases = {
            "FLC": {"local": False, "horizontal": True, "vertical": False},
            "VO": {"local": True, "horizontal": True, "vertical": False},
            "HO": {"local": True, "horizontal": False, "vertical": True},
            "RO": {"local": False, "horizontal": True, "vertical": False},
            "BCO": {"local": False, "horizontal": True, "vertical": False},
        }
        for name, mask in cases.items():
            with self.subTest(name=name):
                context = PolicyContext(observation={}, legal_action_mask=mask, trace_history=("gate2",))
                action = PolicyRegistry.resolve(name).choose_action(context)
                self.assertTrue(context.legal_action_mask[action])

    def test_gate2_mleo_compliance(self) -> None:
        context = PolicyContext(
            observation={
                "mleo_delay_candidates": {
                    "local": {"total_delay": 1.0},
                    "horizontal": {"total_delay": 2.0},
                    "vertical": {"total_delay": 3.0},
                }
            },
            legal_action_mask={"local": False, "horizontal": True, "vertical": True},
            trace_history=("gate2",),
        )
        action = PolicyRegistry.resolve("MLEO").choose_action(context)
        self.assertTrue(context.legal_action_mask[action])

    def test_gate2_no_legal_action_reports_no_choice(self) -> None:
        for name in ("FLC", "VO", "HO", "RO", "BCO", "MLEO"):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    PolicyRegistry.resolve(name).choose_action(
                        PolicyContext(
                            observation={},
                            legal_action_mask={"local": False, "horizontal": False, "vertical": False},
                            trace_history=("gate2",),
                        )
                    )


class Phase0ValidationGate3ROSeeding(unittest.TestCase):
    def test_gate3_ro_seeded_sampling_is_reproducible(self) -> None:
        first = PolicyRegistry.resolve("RO")
        second = PolicyRegistry.resolve("RO")
        context = PolicyContext(
            observation={},
            legal_action_mask={"local": True, "horizontal": False, "vertical": True},
            trace_history=("gate3",),
        )
        first_actions = [first.choose_action(context) for _ in range(8)]
        second_actions = [second.choose_action(context) for _ in range(8)]
        self.assertEqual(first_actions, second_actions)

    def test_gate3_ro_single_action_mask_returns_that_action(self) -> None:
        policy = PolicyRegistry.resolve("RO")
        context = PolicyContext(
            observation={},
            legal_action_mask={"local": False, "horizontal": False, "vertical": True},
            trace_history=("gate3",),
        )
        self.assertEqual([policy.choose_action(context) for _ in range(5)], ["vertical"] * 5)


class Phase0ValidationGate4BCOBalancing(unittest.TestCase):
    def test_gate4_bco_uses_balance_hint_before_rollover(self) -> None:
        policy = PolicyRegistry.resolve("BCO")
        context = PolicyContext(
            observation={"balance_hint": {"local": 3.0, "horizontal": 1.0, "vertical": 2.0}},
            legal_action_mask={"local": True, "horizontal": True, "vertical": True},
            trace_history=("gate4",),
        )
        self.assertEqual(policy.choose_action(context), "horizontal")

    def test_gate4_bco_rotates_over_concrete_placements_in_paper_order(self) -> None:
        policy = PolicyRegistry.resolve("BCO")
        context = PolicyContext(
            observation={
                "local_action": "compute_local",
                "cloud_action": "cloud",
                "horizontal_destinations": ("2", "3"),
            },
            legal_action_mask={"compute_local": True, "cloud": True, "2": True, "3": True},
            trace_history=("gate4",),
        )
        expected = ["compute_local", "cloud", "2", "3", "compute_local"]
        self.assertEqual([policy.choose_action(context) for _ in range(5)], expected)

    def test_gate4_bco_rollover_is_deterministic_and_mask_compliant(self) -> None:
        policy = PolicyRegistry.resolve("BCO")
        context = PolicyContext(
            observation={},
            legal_action_mask={"local": True, "horizontal": True, "vertical": True},
            trace_history=("gate4",),
        )
        self.assertEqual([policy.choose_action(context) for _ in range(5)], ["local", "horizontal", "vertical", "local", "horizontal"])


class Phase0ValidationGate5MLEORanking(unittest.TestCase):
    def test_gate5_mleo_chooses_lowest_delay_candidate(self) -> None:
        policy = PolicyRegistry.resolve("MLEO")
        context = PolicyContext(
            observation={
                "mleo_delay_candidates": {
                    "local": {"queue_delay": 2.0, "transmission_delay": 0.0, "compute_delay": 2.0},
                    "horizontal": {"queue_delay": 1.0, "transmission_delay": 1.0, "compute_delay": 1.0},
                    "vertical": {"queue_delay": 4.0, "transmission_delay": 1.0, "compute_delay": 1.0},
                }
            },
            legal_action_mask={"local": True, "horizontal": True, "vertical": True},
            trace_history=("gate5",),
        )
        self.assertEqual(policy.choose_action(context), "horizontal")

    def test_gate5_mleo_chooses_lowest_placement_candidate(self) -> None:
        policy = PolicyRegistry.resolve("MLEO")
        context = PolicyContext(
            observation={
                "queue_delay_estimates": {"local": 1.0, "cloud": 4.0, "2": 0.5},
                "mleo_placement_candidates": [
                    {"action_id": "local", "action_family": "local", "compute_delay": 1.0},
                    {"action_id": "cloud", "action_family": "vertical", "transmission_delay": 1.0, "compute_delay": 1.0},
                    {"action_id": "2", "action_family": "horizontal", "transmission_delay": 0.5, "compute_delay": 0.5},
                ],
            },
            legal_action_mask={"local": True, "cloud": True, "2": True},
            trace_history=("gate5",),
        )
        self.assertEqual(policy.choose_action(context), "2")

    def test_gate5_mleo_deterministic_tie_handling(self) -> None:
        policy = PolicyRegistry.resolve("MLEO")
        context = PolicyContext(
            observation={
                "mleo_delay_candidates": {
                    "local": {"total_delay": 5.0},
                    "horizontal": {"total_delay": 5.0},
                    "vertical": {"total_delay": 5.0},
                }
            },
            legal_action_mask={"local": True, "horizontal": True, "vertical": True},
            trace_history=("gate5",),
        )
        self.assertEqual(policy.choose_action(context), "local")


class Phase0ValidationGate6MLEOFallback(unittest.TestCase):
    def test_gate6_mleo_missing_fields_use_fallback_hints(self) -> None:
        policy = PolicyRegistry.resolve("MLEO")
        context = PolicyContext(
            observation={"fallback_hints": {"local": 3.0, "horizontal": 1.0, "vertical": 2.0}},
            legal_action_mask={"local": True, "horizontal": True, "vertical": True},
            trace_history=("gate6",),
        )
        self.assertEqual(policy.choose_action(context), "horizontal")

    def test_gate6_mleo_missing_fields_without_hints_use_mask_order(self) -> None:
        policy = PolicyRegistry.resolve("MLEO")
        context = PolicyContext(
            observation={},
            legal_action_mask={"local": False, "horizontal": False, "vertical": True},
            trace_history=("gate6",),
        )
        self.assertEqual(policy.choose_action(context), "vertical")

    def test_gate6_mleo_latency_estimates_still_supported(self) -> None:
        policy = PolicyRegistry.resolve("MLEO")
        context = PolicyContext(
            observation={"latency_estimates": {"local": 9.0, "horizontal": 4.0, "vertical": 5.0}},
            legal_action_mask={"local": True, "horizontal": True, "vertical": True},
            trace_history=("gate6",),
        )
        self.assertEqual(policy.choose_action(context), "horizontal")


class Phase0ValidationGate7ControlledDifferentiation(unittest.TestCase):
    def test_gate7_different_policies_select_different_families_from_same_context(self) -> None:
        context = PolicyContext(
            observation={
                "mleo_delay_candidates": {
                    "local": {"queue_delay": 5.0, "transmission_delay": 0.0, "compute_delay": 5.0},
                    "horizontal": {"queue_delay": 2.0, "transmission_delay": 2.0, "compute_delay": 2.0},
                    "vertical": {"queue_delay": 1.0, "transmission_delay": 1.0, "compute_delay": 1.0},
                },
                "fallback_hints": {"local": 3.0, "horizontal": 2.0, "vertical": 1.0},
            },
            legal_action_mask={"local": True, "horizontal": True, "vertical": True},
            trace_history=("gate7",),
        )
        actions = {name: PolicyRegistry.resolve(name).choose_action(context) for name in ("FLC", "HO", "VO", "MLEO")}
        families = {name: action_family(action) for name, action in actions.items()}
        self.assertEqual(families["FLC"], "local")
        self.assertEqual(families["HO"], "horizontal")
        self.assertEqual(families["VO"], "vertical")
        self.assertEqual(families["MLEO"], "vertical")
        self.assertGreaterEqual(len(set(families.values())), 3)

    def test_gate7_different_policies_select_concrete_placements_from_same_context(self) -> None:
        context = PolicyContext(
            observation={
                "source_agent_id": "1",
                "local_action": "compute_local",
                "cloud_action": "cloud",
                "horizontal_destinations": ("2", "3"),
                "mleo_placement_candidates": [
                    {"action_id": "compute_local", "action_family": "local", "queue_delay": 1.0, "compute_delay": 1.0},
                    {"action_id": "cloud", "action_family": "vertical", "queue_delay": 4.0, "transmission_delay": 1.0, "compute_delay": 1.0},
                    {"action_id": "2", "action_family": "horizontal", "queue_delay": 2.0, "transmission_delay": 1.0, "compute_delay": 1.0},
                    {"action_id": "3", "action_family": "horizontal", "queue_delay": 0.5, "transmission_delay": 0.5, "compute_delay": 0.5},
                ],
                "fallback_hints": {"local": 3.0, "cloud": 2.0, "horizontal": 1.0},
            },
            legal_action_mask={"compute_local": True, "cloud": True, "2": True, "3": True},
            trace_history=("gate7",),
        )
        actions = {name: PolicyRegistry.resolve(name).choose_action(context) for name in ("FLC", "HO", "VO", "BCO", "MLEO")}
        self.assertEqual(actions["FLC"], "compute_local")
        self.assertEqual(actions["VO"], "cloud")
        self.assertEqual(actions["HO"], "2")
        self.assertEqual(actions["BCO"], "compute_local")
        self.assertEqual(actions["MLEO"], "3")


class Phase0ValidationGate8ScopeAudit(unittest.TestCase):
    def test_gate8_forbidden_paths_not_changed(self) -> None:
        forbidden_prefixes = ("src/environment/", "src/training/", "src/agents/", "artifacts/", "resources/")
        current_changed_paths = (
            "src/policies/common.py",
            "src/policies/flc.py",
            "src/policies/ho.py",
            "src/policies/vo.py",
            "src/policies/ro.py",
            "src/policies/bco.py",
            "src/policies/mleo.py",
            "src/evaluation/policy_registry.py",
            "tests/unit/test_policy_registry.py",
            "tests/unit/test_baseline_policy_fidelity.py",
            "tests/unit/test_mleo_policy.py",
            "tests/integration/test_baseline_policy_fidelity_flow.py",
            "tests/unit/test_phase0_validation_gates.py",
            "scripts/validation/run_phase0_gates.py",
        )
        violations = [p for p in current_changed_paths if p.startswith(forbidden_prefixes)]
        self.assertFalse(violations, f"Forbidden paths changed: {violations}")

    def test_gate8_new_validation_gate_files_are_in_allowed_scope(self) -> None:
        allowed_prefixes = ("tests/", "scripts/validation/", "docs/plans/", "docs/run-logs/")
        new_files = (
            "tests/unit/test_phase0_validation_gates.py",
            "scripts/validation/run_phase0_gates.py",
            "docs/plans/2026-06-28-validation-gate-implementation.md",
        )
        violations = [f for f in new_files if not any(f.startswith(p) for p in allowed_prefixes)]
        self.assertFalse(violations, f"Files outside allowed scope: {violations}")


if __name__ == "__main__":
    unittest.main()
