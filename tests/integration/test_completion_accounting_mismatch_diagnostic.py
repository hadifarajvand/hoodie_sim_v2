# Test Completion Accounting Mismatch Diagnostic

"""
Integration tests for completion_accounting_mismatch_diagnostic.py
"""

import pytest
from typing import Dict, List
from src.analysis.completion_accounting_mismatch_diagnostic import (
    diagnose,
    format_evidence,
    run_completion_accounting_mismatch_diagnostic,
    DiagnosticOutput,
    classify_accounting,
)


class TestCompletionAccountingMismatchDiagnostic:

    def test_execution_completed_then_dropped(self):
        """Test verdict when execution_completed tasks are dropped and trainer counted correctly."""
        lifecycle_events = [
            {"event_type": "task_arrived", "slot": 1, "task_id": "task1", "episode_id": 1},
            {"event_type": "execution_started", "slot": 2, "task_id": "task1", "episode_id": 1},
            {"event_type": "execution_completed", "slot": 5, "task_id": "task1", "episode_id": 1},
            {"event_type": "deadline_expired", "slot": 6, "task_id": "task1", "episode_id": 1},
            {"event_type": "task_dropped", "slot": 7, "task_id": "task1", "episode_id": 1},
        ]

        finalized_tasks = [{
            "task_id": "task1",
            "terminal_outcome": "expired",
            "completion_slot": None,
            "drop_slot": 7
        }]

        result = diagnose(
            timing_audit={},
            lifecycle_events=lifecycle_events,
            finalized_tasks=finalized_tasks,
            trainer_completed=0,
            trainer_dropped=1
        )

        assert result["verdict"] == "diagnostic_no_repair_needed_update_interpretation"
        # Trainer count matches finalized tasks — no mismatch
        assert len(result["mismatch_table"]) == 0

    def test_execution_completed_without_finalized_task(self):
        """Test verdict when execution_completed task has no finalized_task."""
        lifecycle_events = [
            {"event_type": "task_arrived", "slot": 1, "task_id": "task1", "episode_id": 1},
            {"event_type": "execution_started", "slot": 2, "task_id": "task1", "episode_id": 1},
            {"event_type": "execution_completed", "slot": 5, "task_id": "task1", "episode_id": 1},
        ]

        finalized_tasks = []

        result = diagnose(
            timing_audit={},
            lifecycle_events=lifecycle_events,
            finalized_tasks=finalized_tasks,
            trainer_completed=0,
            trainer_dropped=0
        )

        assert result["verdict"] == "diagnostic_needs_environment_finalization_repair"
        assert len(result["mismatch_table"]) == 1
        assert result["mismatch_table"][0]["classification"] == "execution_completed_without_finalized_task"

    def test_finalized_completed_missed_by_trainer(self):
        """Test aggregate mismatch when trainer counted 0 but finalized says 1 completed."""
        lifecycle_events = [
            {"event_type": "task_arrived", "slot": 1, "task_id": "task1", "episode_id": 1},
            {"event_type": "execution_started", "slot": 2, "task_id": "task1", "episode_id": 1},
            {"event_type": "execution_completed", "slot": 5, "task_id": "task1", "episode_id": 1},
        ]

        finalized_tasks = [{
            "task_id": "task1",
            "terminal_outcome": "completed",
            "completion_slot": 5,
            "drop_slot": None
        }]

        result = diagnose(
            timing_audit={},
            lifecycle_events=lifecycle_events,
            finalized_tasks=finalized_tasks,
            trainer_completed=0,
            trainer_dropped=0
        )

        # Aggregate mismatch: trainer_completed (0) != expected_completed (1)
        assert result["verdict"] == "diagnostic_needs_trainer_accounting_repair"
        assert result["accounting_summary"]["aggregate_completed_diff"] == -1
        assert result["accounting_summary"]["aggregate_dropped_diff"] == 0
        # No per-task mismatch (task1 has both lifecycle events and finalized task)
        assert len(result["mismatch_table"]) == 0

    def test_format_evidence_output_shape(self):
        """Test that format_evidence produces valid markdown."""
        diagnostic_output: DiagnosticOutput = {
            "task_lifecycle_rows": [
                {
                    "task_id": "task1",
                    "episode_id": 1,
                    "first_arrival_slot": 1,
                    "service_start_slot": 2,
                    "execution_completed_slot": 5,
                    "deadline_reached_slot": None,
                    "deadline_expired_slot": 6,
                    "task_completed_slot": None,
                    "task_dropped_slot": 7,
                    "reward_emitted_slot": 8,
                    "finalized_task_exists": True,
                    "finalized_terminal_outcome": "expired",
                    "finalized_completion_slot": None,
                    "finalized_drop_slot": 7,
                    "trainer_counted_completed": False,
                    "trainer_counted_dropped": True,
                    "accounting_classification": "execution_completed_then_dropped"
                }
            ],
            "mismatch_table": [
                {
                    "task_id": "task1",
                    "execution_completed_exists": True,
                    "finalized_task_exists": True,
                    "finalized_terminal_outcome": "expired",
                    "counted_by_trainer": "dropped",
                    "classification": "execution_completed_then_dropped"
                }
            ],
            "accounting_summary": {
                "execution_completed_count": 1,
                "lifecycle_task_completed_count": 0,
                "lifecycle_task_dropped_count": 1,
                "finalized_completed_count": 0,
                "finalized_dropped_count": 1,
                "trainer_completed_task_count": 0,
                "trainer_dropped_task_count": 1,
                "execution_completed_task_ids": ["task1"],
                "finalized_completed_task_ids": [],
                "finalized_dropped_task_ids": ["task1"],
                "mismatch_task_ids": ["task1"],
                "orphan_finalized_task_ids": [],
                "aggregate_completed_diff": 0,
                "aggregate_dropped_diff": 0
            },
            "verdict": "diagnostic_no_repair_needed_update_interpretation"
        }

        evidence = format_evidence(diagnostic_output)
        assert "# Completion Accounting Mismatch Diagnostic Evidence" in evidence
        assert "execution_completed_count: 1" in evidence
        assert "finalized_dropped_count: 1" in evidence
        assert "aggregate_dropped_diff: 0" in evidence
        assert "orphan_finalized_task_ids" in evidence
        assert "| task1 | ✓ | ✓ | expired | dropped | execution_completed_then_dropped |" in evidence
        assert "- **verdict**: `diagnostic_no_repair_needed_update_interpretation`" in evidence

    def test_empty_diagnostic_output(self):
        """Test diagnostic with no events."""
        result = diagnose(
            timing_audit={},
            lifecycle_events=[],
            finalized_tasks=[],
            trainer_completed=0,
            trainer_dropped=0
        )

        assert result["verdict"] == "diagnostic_inconclusive"
        assert len(result["task_lifecycle_rows"]) == 0
        assert len(result["mismatch_table"]) == 0

    def test_classify_accounting_utility(self):
        """Test classify_accounting helper covers all branches."""
        # execution_completed_then_dropped
        assert classify_accounting(5, "dropped", "dropped") == "execution_completed_then_dropped"
        assert classify_accounting(5, "expired", "dropped") == "execution_completed_then_dropped"
        assert classify_accounting(5, "dropped", "unknown") == "execution_completed_then_dropped"
        assert classify_accounting(5, "expired", "completed") == "execution_completed_then_dropped"

        # execution_completed_then_completed
        assert classify_accounting(5, "completed", "completed") == "execution_completed_then_completed"

        # finalized_completed_missed_by_trainer
        assert classify_accounting(5, "completed", "dropped") == "finalized_completed_missed_by_trainer"
        assert classify_accounting(5, "completed", "unknown") == "finalized_completed_missed_by_trainer"

        # execution_completed_without_finalized_task
        assert classify_accounting(5, None, "unknown") == "execution_completed_without_finalized_task"

        # lifecycle_finalized_disagreement
        assert classify_accounting(5, "something_else", "completed") == "lifecycle_finalized_disagreement"

        # pending_or_unknown
        assert classify_accounting(None, None, "unknown") == "pending_or_unknown"

    def test_integration_with_runner(self):
        """Run the bounded diagnostic against the real environment."""
        output = run_completion_accounting_mismatch_diagnostic(
            episodes=1,
            episode_length=20,
        )
        assert "verdict" in output
        assert "task_lifecycle_rows" in output
        assert "accounting_summary" in output
        summary = output["accounting_summary"]
        assert "execution_completed_count" in summary
        assert "trainer_completed_task_count" in summary
        assert "trainer_dropped_task_count" in summary
        assert "mismatch_task_ids" in summary
