from __future__ import annotations

import unittest

from src.environment.paper_timeout import compute_absolute_deadline, is_success_before_deadline, terminal_status_from_completion


class RuntimePaperFaithfulSemanticsAlignmentDeadlineTests(unittest.TestCase):
    def test_absolute_deadline_uses_phi_minus_one(self) -> None:
        self.assertEqual(compute_absolute_deadline(1, 4), 4)

    def test_paper_mode_is_strict_before_deadline(self) -> None:
        self.assertTrue(is_success_before_deadline(3, 1, 4))
        self.assertFalse(is_success_before_deadline(4, 1, 4))
        self.assertFalse(is_success_before_deadline(5, 1, 4))
        self.assertFalse(is_success_before_deadline(None, 1, 4))

    def test_compatibility_mode_allows_equality_at_deadline_when_explicit(self) -> None:
        self.assertTrue(is_success_before_deadline(4, 1, 4, mode="compatibility"))
        self.assertFalse(is_success_before_deadline(5, 1, 4, mode="compatibility"))

    def test_terminal_status_from_completion_uses_completion_kind_mapping(self) -> None:
        self.assertEqual(terminal_status_from_completion(3, 1, 4, completion_kind="private"), "completed_private")
        self.assertEqual(terminal_status_from_completion(3, 1, 4, completion_kind="public"), "completed_public")
        self.assertEqual(terminal_status_from_completion(3, 1, 4, completion_kind="cloud"), "completed_cloud")
        self.assertEqual(terminal_status_from_completion(4, 1, 4, completion_kind="private"), "dropped_timeout")

    def test_invalid_runtime_mode_rejected(self) -> None:
        with self.assertRaises(ValueError):
            is_success_before_deadline(3, 1, 4, mode="legacy")

    def test_invalid_completion_kind_rejected(self) -> None:
        with self.assertRaises(ValueError):
            terminal_status_from_completion(3, 1, 4, completion_kind="edge")


if __name__ == "__main__":
    unittest.main()
