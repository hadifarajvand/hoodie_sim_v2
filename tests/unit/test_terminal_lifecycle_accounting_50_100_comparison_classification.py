from __future__ import annotations

import unittest

from src.analysis.terminal_lifecycle_accounting_50_100_comparison.lifecycle_classifier import (
    canonical_task_key,
    classify_event_type,
    terminal_outcome_from_event_types,
)


class TerminalLifecycleAccounting50_100ComparisonClassificationTests(unittest.TestCase):
    def test_terminal_outcome_and_lifecycle_event_types_are_separated(self) -> None:
        self.assertEqual(classify_event_type("task_completed"), "terminal_outcome_event")
        self.assertEqual(classify_event_type("task_dropped"), "terminal_outcome_event")
        self.assertEqual(classify_event_type("deadline_reached"), "lifecycle_event_only")
        self.assertEqual(classify_event_type("deadline_expired"), "lifecycle_event_only")
        self.assertEqual(classify_event_type("reward_emitted"), "reward_event")
        self.assertEqual(classify_event_type("execution_completed"), "lifecycle_event_only")

    def test_canonical_terminal_outcome_prefers_completed_then_dropped_then_pending(self) -> None:
        self.assertEqual(terminal_outcome_from_event_types({"task_completed", "task_dropped"}, pending_evidence=False), "completed")
        self.assertEqual(terminal_outcome_from_event_types({"task_dropped"}, pending_evidence=False), "dropped")
        self.assertEqual(terminal_outcome_from_event_types(set(), pending_evidence=True), "pending_at_horizon")
        self.assertEqual(terminal_outcome_from_event_types(set(), pending_evidence=False), "unknown")

    def test_canonical_task_key_uses_trace_episode_task_identity(self) -> None:
        self.assertEqual(canonical_task_key("trace-1", 7, 42), "trace-1:7:42")


if __name__ == "__main__":
    unittest.main()
