from __future__ import annotations

import inspect
import unittest

import src.environment.deadline_rules as deadline_rules_module
import src.environment.paper_timeout as paper_timeout_module
from src.environment.deadline_rules import has_expired
from src.environment.paper_timeout import build_timeout_contract, compute_absolute_deadline, is_success_before_deadline, terminal_status_from_completion
from src.environment.task import Task


class RuntimePaperFaithfulSemanticsAlignmentDeadlineTests(unittest.TestCase):
    def test_absolute_deadline_uses_phi_minus_one(self) -> None:
        self.assertEqual(compute_absolute_deadline(1, 4), 4)

    def test_paper_mode_is_strict_before_deadline(self) -> None:
        self.assertTrue(is_success_before_deadline(3, 1, 4))
        self.assertFalse(is_success_before_deadline(4, 1, 4))
        self.assertFalse(is_success_before_deadline(5, 1, 4))
        self.assertFalse(is_success_before_deadline(None, 1, 4))

    def test_build_timeout_contract_defaults_to_paper_strictness(self) -> None:
        contract = build_timeout_contract(arrival_slot=1, timeout_phi=4, completion_slot=4)
        self.assertTrue(contract.dropped_due_to_timeout)
        self.assertEqual(contract.deadline_slot, 4)

    def test_build_timeout_contract_explicit_compatibility_preserves_equality_at_deadline(self) -> None:
        contract = build_timeout_contract(arrival_slot=1, timeout_phi=4, completion_slot=4, mode="compatibility")
        self.assertFalse(contract.dropped_due_to_timeout)
        self.assertEqual(contract.deadline_slot, 4)

    def test_compatibility_mode_allows_equality_at_deadline_when_explicit(self) -> None:
        self.assertTrue(is_success_before_deadline(4, 1, 4, mode="compatibility"))
        self.assertFalse(is_success_before_deadline(5, 1, 4, mode="compatibility"))

    def test_terminal_status_from_completion_uses_completion_kind_mapping(self) -> None:
        self.assertEqual(terminal_status_from_completion(3, 1, 4, completion_kind="private"), "completed_private")
        self.assertEqual(terminal_status_from_completion(3, 1, 4, completion_kind="public"), "completed_public")
        self.assertEqual(terminal_status_from_completion(3, 1, 4, completion_kind="cloud"), "completed_cloud")
        self.assertEqual(terminal_status_from_completion(4, 1, 4, completion_kind="private"), "dropped_timeout")

    def test_deadline_rules_defaults_to_paper_strict_expiration(self) -> None:
        task = Task(
            task_id=1,
            source_agent_id=1,
            arrival_slot=1,
            size=1.0,
            processing_density=1.0,
            timeout_length=3,
            absolute_deadline_slot=4,
        )
        self.assertTrue(has_expired(task, current_slot=4))
        self.assertFalse(has_expired(task, current_slot=4, mode="compatibility"))

    def test_invalid_runtime_mode_rejected(self) -> None:
        with self.assertRaises(ValueError):
            is_success_before_deadline(3, 1, 4, mode="legacy")

    def test_invalid_completion_kind_rejected(self) -> None:
        with self.assertRaises(ValueError):
            terminal_status_from_completion(3, 1, 4, completion_kind="edge")

    def test_no_hidden_compatibility_shims_exist_in_deadline_modules(self) -> None:
        self.assertFalse(hasattr(paper_timeout_module, "_LEGACY_COMPATIBILITY_CALLERS"))
        self.assertFalse(hasattr(deadline_rules_module, "_LEGACY_COMPATIBILITY_CALLERS"))
        self.assertNotIn("inspect.currentframe", inspect.getsource(paper_timeout_module))
        self.assertNotIn("inspect.currentframe", inspect.getsource(deadline_rules_module))
        self.assertEqual(paper_timeout_module.build_timeout_contract.__kwdefaults__["mode"], "paper")
        self.assertEqual(deadline_rules_module.has_expired.__defaults__, ("paper",))


if __name__ == "__main__":
    unittest.main()
