from __future__ import annotations

import math
import unittest

from src.environment.reward_timing import (
    can_emit_reward,
    phi_private,
    phi_public,
    reward_from_terminal_state,
    reward_slot_for_terminal,
    select_phi,
    validate_terminal_state,
)


class RuntimePaperFaithfulSemanticsAlignmentRewardTests(unittest.TestCase):
    def test_terminal_state_consistency_rules_are_explicit(self) -> None:
        validate_terminal_state("completed_private", 7, None)
        validate_terminal_state("completed_public", 7, None)
        validate_terminal_state("completed_cloud", 7, None)
        validate_terminal_state("dropped_timeout", 7, "deadline_exceeded")
        validate_terminal_state("dropped_unavailable", 7, "destination_unavailable")
        validate_terminal_state("pending", None, None)

        with self.assertRaises(ValueError):
            validate_terminal_state("completed_private", 7, "deadline_exceeded")
        with self.assertRaises(ValueError):
            validate_terminal_state("dropped_timeout", None, "deadline_exceeded")
        with self.assertRaises(ValueError):
            validate_terminal_state("dropped_unavailable", 7, None)
        with self.assertRaises(ValueError):
            validate_terminal_state("pending", 7, None)

        self.assertTrue(can_emit_reward("completed_private"))
        self.assertTrue(can_emit_reward("dropped_timeout"))
        self.assertFalse(can_emit_reward("pending"))

    def test_reward_equation_twenty_is_explicit(self) -> None:
        self.assertTrue(math.isnan(reward_from_terminal_state(False, "completed_private", 4, 40)))
        self.assertEqual(reward_from_terminal_state(True, "completed_private", 4, 40), -4.0)
        self.assertEqual(reward_from_terminal_state(True, "dropped_timeout", 4, 40), -40.0)
        with self.assertRaises(ValueError):
            reward_from_terminal_state(True, "pending", 4, 40)

    def test_reward_equation_twenty_one_selects_private_or_public_phi(self) -> None:
        self.assertEqual(select_phi(True, 4, 5), 4)
        self.assertEqual(select_phi(1, 4, 5), 4)
        self.assertEqual(select_phi(False, 4, 5), 5)
        self.assertEqual(select_phi(0, 4, 5), 5)

    def test_reward_equation_twenty_two_private_phi_example(self) -> None:
        self.assertEqual(phi_private(psi_priv=5, t=2), 4)

    def test_reward_equation_twenty_three_public_phi_example(self) -> None:
        self.assertEqual(phi_public(((1, 6), (0, 9)), t=2), 5)
        self.assertEqual(phi_public(((False, 10), (True, 8), (0, 12)), t=2), 7)

    def test_reward_slot_and_terminal_evidence_are_explicit(self) -> None:
        self.assertEqual(reward_slot_for_terminal(5), 6)


if __name__ == "__main__":
    unittest.main()
