"""
Phase 0, Part 3: Verify all 6 baseline policies implement correct legality per paper spec.

Paper baseline definitions:
- FLC (Full Local Computing): always local if legal
- RO (Random Offloading): uniform random over legal actions
- HO (Horizontal Offloading): uniform random over horizontal destinations
- VO (Vertical Offloading): always vertical to cloud if legal
- BCO (Balanced Cooperation Offloading): round-robin over [local, cloud, horizontal]
- MLEO (Minimum Latency Estimate Offloading): compute delay for each option, pick min
"""

import random
import unittest

from src.policies.policy_interface import PolicyContext
from src.policies.common import (
    FAMILY_ACTIONS,
    FALLBACK_FAMILY_ORDER,
    action_family,
    first_legal_action,
    first_legal_family_action,
    first_legal_placement_action,
    legal_actions,
    legal_family_available,
    legal_placement_available,
    placement_actions_for_family,
)
from src.policies.flc import FullLocalComputingPolicy
from src.policies.ro import RandomOffloadingPolicy
from src.policies.ho import HorizontalOffloadingPolicy
from src.policies.vo import VerticalOffloadingPolicy
from src.policies.bco import BalancedCooperationOffloadingPolicy
from src.policies.mleo import MinimumLatencyEstimateOffloadingPolicy


def _make_context(
    legal_mask: dict[str, bool],
    observation: dict | None = None,
) -> PolicyContext:
    """Helper to create a PolicyContext with given legal action mask and observation."""
    return PolicyContext(
        observation=observation or {},
        legal_action_mask=legal_mask,
        trace_history=(),
    )


# ── Common helpers ──────────────────────────────────────────────────────

class TestCommonHelpers(unittest.TestCase):
    """Test the common helper functions used by all policies."""

    def test_action_family_classification(self) -> None:
        """Action family classification must match paper action space."""
        self.assertEqual(action_family("local"), "local")
        self.assertEqual(action_family("compute_local"), "local")
        self.assertEqual(action_family("horizontal"), "horizontal")
        self.assertEqual(action_family("offload_horizontal"), "horizontal")
        self.assertEqual(action_family("vertical"), "vertical")
        self.assertEqual(action_family("offload_vertical"), "vertical")

    def test_legal_actions_filters_by_mask(self) -> None:
        """legal_actions must return only actions with True in mask."""
        mask = {"local": True, "horizontal": False, "vertical": True}
        context = _make_context(mask)
        self.assertEqual(set(legal_actions(context)), {"local", "vertical"})

    def test_legal_actions_empty_when_all_false(self) -> None:
        """legal_actions must return empty tuple when no actions are legal."""
        mask = {"local": False, "horizontal": False, "vertical": False}
        context = _make_context(mask)
        self.assertEqual(legal_actions(context), ())

    def test_first_legal_action_respects_preference_order(self) -> None:
        """first_legal_action must return the first preferred action that is legal."""
        mask = {"local": False, "horizontal": True, "vertical": True}
        context = _make_context(mask)
        self.assertEqual(first_legal_action(context), "horizontal")

    def test_first_legal_action_raises_on_empty(self) -> None:
        """first_legal_action must raise ValueError when no actions are legal."""
        mask = {"local": False, "horizontal": False, "vertical": False}
        context = _make_context(mask)
        with self.assertRaises(ValueError):
            first_legal_action(context)

    def test_first_legal_family_action_returns_none_when_not_available(self) -> None:
        """first_legal_family_action must return None when family has no legal actions."""
        mask = {"local": False, "horizontal": False, "vertical": False}
        context = _make_context(mask)
        self.assertIsNone(first_legal_family_action(context, "local"))

    def test_placement_actions_for_family_local(self) -> None:
        """placement_actions_for_family('local') must return local actions."""
        mask = {"local": True, "compute_local": True, "horizontal": False, "vertical": False}
        context = _make_context(mask)
        actions = placement_actions_for_family(context, "local")
        self.assertTrue(len(actions) > 0)
        for action in actions:
            self.assertIn(action, ("local", "compute_local"))


# ── FLC: Full Local Computing ──────────────────────────────────────────

class TestFLCBaseline(unittest.TestCase):
    """FLC must always choose local compute when legal."""

    def setUp(self) -> None:
        self.policy = FullLocalComputingPolicy()

    def test_flc_chooses_local_when_legal(self) -> None:
        """FLC must choose 'local' when local is legal."""
        context = _make_context({"local": True, "horizontal": True, "vertical": True})
        action = self.policy.choose_action(context)
        self.assertIn(action, ("local", "compute_local"))

    def test_flc_chooses_local_when_only_local_is_legal(self) -> None:
        """FLC must choose 'local' when it's the only legal action."""
        context = _make_context({"local": True, "horizontal": False, "vertical": False})
        action = self.policy.choose_action(context)
        self.assertIn(action, ("local", "compute_local"))

    def test_flc_falls_back_when_local_illegal(self) -> None:
        """FLC must fall back to next legal action when local is not legal."""
        context = _make_context({"local": False, "horizontal": True, "vertical": True})
        action = self.policy.choose_action(context)
        self.assertIn(action, ("horizontal", "offload_horizontal", "vertical", "offload_vertical"))

    def test_flc_raises_on_no_legal_actions(self) -> None:
        """FLC must raise an error when no actions are legal."""
        context = _make_context({"local": False, "horizontal": False, "vertical": False})
        with self.assertRaises(ValueError):
            self.policy.choose_action(context)


# ── RO: Random Offloading ──────────────────────────────────────────────

class TestROBaseline(unittest.TestCase):
    """RO must choose uniformly at random among legal actions."""

    def setUp(self) -> None:
        self.policy = RandomOffloadingPolicy(seed=42)

    def test_ro_chooses_legal_action(self) -> None:
        """RO must always select an action from the legal set."""
        for _ in range(50):
            context = _make_context({"local": True, "horizontal": True, "vertical": True})
            action = self.policy.choose_action(context)
            self.assertIn(action, ("local", "compute_local", "horizontal", "offload_horizontal", "vertical", "offload_vertical"))

    def test_ro_respects_legal_actions_only(self) -> None:
        """RO must never select an action marked as illegal."""
        for _ in range(50):
            context = _make_context({"local": True, "horizontal": False, "vertical": False})
            action = self.policy.choose_action(context)
            self.assertIn(action, ("local", "compute_local"))

    def test_ro_uses_all_families_over_multiple_calls(self) -> None:
        """RO must eventually explore all legal action families."""
        context = _make_context({"local": True, "horizontal": True, "vertical": True})
        seen_families: set[str] = set()
        for _ in range(100):
            action = self.policy.choose_action(context)
            seen_families.add(action_family(action))
        self.assertEqual(seen_families, {"local", "horizontal", "vertical"})

    def test_ro_raises_on_no_legal_actions(self) -> None:
        """RO must raise error when no legal actions exist."""
        context = _make_context({"local": False, "horizontal": False, "vertical": False})
        with self.assertRaises(ValueError):
            self.policy.choose_action(context)


# ── HO: Horizontal Offloading ──────────────────────────────────────────

class TestHOBaseline(unittest.TestCase):
    """HO must prefer horizontal offloading when legal."""

    def setUp(self) -> None:
        self.policy = HorizontalOffloadingPolicy()

    def test_ho_chooses_horizontal_when_legal(self) -> None:
        """HO must choose a horizontal action when horizontal is legal."""
        context = _make_context({"local": True, "horizontal": True, "vertical": True})
        action = self.policy.choose_action(context)
        self.assertIn(action, ("horizontal", "offload_horizontal"))

    def test_ho_falls_back_when_horizontal_illegal(self) -> None:
        """HO must fall back when horizontal is not legal."""
        context = _make_context({"local": True, "horizontal": False, "vertical": True})
        action = self.policy.choose_action(context)
        self.assertIn(action, ("local", "compute_local", "vertical", "offload_vertical"))
        self.assertNotIn(action, ("horizontal", "offload_horizontal"))

    def test_ho_falls_back_to_local_first(self) -> None:
        """HO must fall back to local before vertical."""
        context = _make_context({"local": True, "horizontal": False, "vertical": True})
        action = self.policy.choose_action(context)
        self.assertIn(action, ("local", "compute_local"))


# ── VO: Vertical Offloading ────────────────────────────────────────────

class TestVOBaseline(unittest.TestCase):
    """VO must prefer vertical offloading (cloud) when legal."""

    def setUp(self) -> None:
        self.policy = VerticalOffloadingPolicy()

    def test_vo_chooses_vertical_when_legal(self) -> None:
        """VO must choose a vertical action when vertical is legal."""
        context = _make_context({"local": True, "horizontal": True, "vertical": True})
        action = self.policy.choose_action(context)
        self.assertIn(action, ("vertical", "offload_vertical"))

    def test_vo_falls_back_when_vertical_illegal(self) -> None:
        """VO must fall back when vertical is not legal."""
        context = _make_context({"local": True, "horizontal": True, "vertical": False})
        action = self.policy.choose_action(context)
        self.assertNotIn(action, ("vertical", "offload_vertical"))

    def test_vo_falls_back_to_local_first(self) -> None:
        """VO must fall back to local before horizontal."""
        context = _make_context({"local": True, "horizontal": True, "vertical": False})
        action = self.policy.choose_action(context)
        self.assertIn(action, ("local", "compute_local"))


# ── BCO: Balanced Cooperation Offloading ───────────────────────────────

class TestBCOBaseline(unittest.TestCase):
    """BCO must round-robin over [local, cloud, horizontal] in that order."""

    def setUp(self) -> None:
        self.policy = BalancedCooperationOffloadingPolicy()

    def test_bco_cycles_through_families(self) -> None:
        """BCO must cycle through local, vertical, horizontal order."""
        context = _make_context({"local": True, "horizontal": True, "vertical": True})
        actions = [self.policy.choose_action(context) for _ in range(6)]
        # With 3 families and round-robin, all families must appear
        families_seen = {action_family(a) for a in actions}
        self.assertEqual(families_seen, {"local", "horizontal", "vertical"})

    def test_bco_respects_legal_mask(self) -> None:
        """BCO must not select illegal actions but still cycle."""
        # Only local and vertical are legal
        context = _make_context({"local": True, "horizontal": False, "vertical": True})
        actions = [self.policy.choose_action(context) for _ in range(10)]
        for action in actions:
            self.assertNotIn(action, ("horizontal", "offload_horizontal"))

    def test_bco_raises_on_no_legal_actions(self) -> None:
        """BCO must raise error when no legal actions exist."""
        context = _make_context({"local": False, "horizontal": False, "vertical": False})
        with self.assertRaises(ValueError):
            self.policy.choose_action(context)


# ── MLEO: Minimum Latency Estimate Offloading ──────────────────────────

class TestMLEOBaseline(unittest.TestCase):
    """MLEO must compute delay for each option and pick the minimum."""

    def setUp(self) -> None:
        self.policy = MinimumLatencyEstimateOffloadingPolicy()

    def test_mleo_uses_latency_estimates(self) -> None:
        """MLEO must prefer the action with lowest latency estimate."""
        observations = {
            "latency_estimates": {"local": 5.0, "horizontal": 2.0, "vertical": 10.0},
        }
        context = _make_context({"local": True, "horizontal": True, "vertical": True}, observations)
        action = self.policy.choose_action(context)
        self.assertIn(action_family(action), {"horizontal"})  # horizontal has lowest latency

    def test_mleo_falls_back_to_legal_without_estimates(self) -> None:
        """MLEO must fall back to a legal action when no latency estimates exist."""
        context = _make_context({"local": True, "horizontal": True, "vertical": True})
        action = self.policy.choose_action(context)
        self.assertIn(action_family(action), {"local", "horizontal", "vertical"})

    def test_mleo_respects_legal_mask_with_estimates(self) -> None:
        """MLEO must not choose an action that's illegal even if it has low latency."""
        observations = {
            "latency_estimates": {"local": 5.0, "horizontal": 1.0, "vertical": 10.0},
        }
        # horizontal illegal despite lowest latency
        context = _make_context({"local": True, "horizontal": False, "vertical": True}, observations)
        action = self.policy.choose_action(context)
        self.assertNotIn(action, ("horizontal", "offload_horizontal"))

    def test_mleo_fallback_reason_documented(self) -> None:
        """MLEO must document the fallback reason when no comparable candidates exist."""
        context = _make_context({"local": True, "horizontal": True, "vertical": True})
        self.policy.choose_action(context)
        self.assertIsNotNone(self.policy.last_fallback_reason)


if __name__ == "__main__":
    unittest.main()
