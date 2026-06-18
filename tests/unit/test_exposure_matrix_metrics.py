from __future__ import annotations

import unittest
from unittest.mock import patch

from src.analysis.exposure_matrix_review import ExposureDecisionRecord, build_exposure_matrix_report
from src.analysis.exposure_matrix_review.model import build_illegal_action_summary, selected_action_is_illegal


class ExposureMatrixMetricsUnitTests(unittest.TestCase):
    def test_selected_illegal_action_rate_uses_selected_action_count_denominator(self) -> None:
        records = [
            ExposureDecisionRecord(
                run_id="run-1",
                strategy="environment_default_policy_probe",
                seed=0,
                decision_opportunity_index=1,
                generated_task_id=1,
                admitted_slot=0,
                selected_action="local",
                legal_local=False,
                legal_horizontal=True,
                legal_vertical=True,
                selected_was_legal=False,
                destination="self",
                queue_type="private",
                terminal_outcome="dropped",
                reward_available=True,
                pending_at_horizon=False,
                task_age_slots=1,
                wait_slots=0,
                execution_progress_slots=0,
                transmission_delay_slots=None,
                evidence_source="trace",
            ),
            ExposureDecisionRecord(
                run_id="run-1",
                strategy="environment_default_policy_probe",
                seed=0,
                decision_opportunity_index=2,
                generated_task_id=2,
                admitted_slot=1,
                selected_action="horizontal",
                legal_local=True,
                legal_horizontal=False,
                legal_vertical=True,
                selected_was_legal=False,
                destination="neighbor",
                queue_type="public",
                terminal_outcome="dropped",
                reward_available=True,
                pending_at_horizon=False,
                task_age_slots=2,
                wait_slots=1,
                execution_progress_slots=0,
                transmission_delay_slots=1,
                evidence_source="trace",
            ),
            ExposureDecisionRecord(
                run_id="run-1",
                strategy="environment_default_policy_probe",
                seed=0,
                decision_opportunity_index=3,
                generated_task_id=3,
                admitted_slot=2,
                selected_action="vertical",
                legal_local=True,
                legal_horizontal=True,
                legal_vertical=False,
                selected_was_legal=False,
                destination="cloud",
                queue_type="cloud",
                terminal_outcome="dropped",
                reward_available=True,
                pending_at_horizon=False,
                task_age_slots=3,
                wait_slots=1,
                execution_progress_slots=0,
                transmission_delay_slots=2,
                evidence_source="trace",
            ),
            ExposureDecisionRecord(
                run_id="run-1",
                strategy="environment_default_policy_probe",
                seed=0,
                decision_opportunity_index=4,
                generated_task_id=4,
                admitted_slot=3,
                selected_action="illegal_action",
                legal_local=True,
                legal_horizontal=True,
                legal_vertical=True,
                selected_was_legal=False,
                destination=None,
                queue_type="private",
                terminal_outcome="dropped",
                reward_available=True,
                pending_at_horizon=False,
                task_age_slots=4,
                wait_slots=1,
                execution_progress_slots=0,
                transmission_delay_slots=None,
                evidence_source="trace",
            ),
            ExposureDecisionRecord(
                run_id="run-1",
                strategy="environment_default_policy_probe",
                seed=0,
                decision_opportunity_index=5,
                generated_task_id=5,
                admitted_slot=4,
                selected_action=None,
                legal_local=True,
                legal_horizontal=True,
                legal_vertical=True,
                selected_was_legal=None,
                destination=None,
                queue_type="private",
                terminal_outcome="pending",
                reward_available=False,
                pending_at_horizon=True,
                task_age_slots=5,
                wait_slots=1,
                execution_progress_slots=0,
                transmission_delay_slots=None,
                evidence_source="trace",
                selected_action_available=True,
            ),
        ]
        summary = build_illegal_action_summary(records, legal_evidence_available=True)
        self.assertEqual(summary.selected_illegal_action_count, 5)
        self.assertEqual(summary.selected_illegal_local_count, 1)
        self.assertEqual(summary.selected_illegal_horizontal_count, 1)
        self.assertEqual(summary.selected_illegal_vertical_count, 1)
        self.assertEqual(summary.selected_illegal_action_rate, 1.0)
        self.assertTrue(summary.selected_illegal_action_examples)
        self.assertEqual(summary.evidence_status, "available")

    def test_selected_illegal_action_count_null_when_legal_evidence_unavailable(self) -> None:
        summary = build_illegal_action_summary([], legal_evidence_available=False)
        self.assertIsNone(summary.selected_illegal_action_count)
        self.assertIsNone(summary.selected_illegal_action_rate)
        self.assertEqual(summary.selected_illegal_action_examples, [])
        self.assertEqual(summary.evidence_status, "unavailable")

    def test_selected_action_is_illegal_detects_unsupported_and_missing_actions(self) -> None:
        unsupported = ExposureDecisionRecord(
            run_id="run",
            strategy="mixed_legal_round_robin_probe",
            seed=1,
            decision_opportunity_index=1,
            generated_task_id=1,
            admitted_slot=0,
            selected_action="outside_set",
            legal_local=True,
            legal_horizontal=True,
            legal_vertical=True,
            selected_was_legal=False,
            destination=None,
            queue_type="private",
            terminal_outcome="dropped",
            reward_available=True,
            pending_at_horizon=False,
            task_age_slots=0,
            wait_slots=0,
            execution_progress_slots=0,
            transmission_delay_slots=None,
            evidence_source="trace",
        )
        missing = ExposureDecisionRecord(
            run_id="run",
            strategy="mixed_legal_round_robin_probe",
            seed=1,
            decision_opportunity_index=2,
            generated_task_id=2,
            admitted_slot=0,
            selected_action=None,
            legal_local=True,
            legal_horizontal=True,
            legal_vertical=True,
            selected_was_legal=None,
            destination=None,
            queue_type="private",
            terminal_outcome="dropped",
            reward_available=True,
            pending_at_horizon=False,
            task_age_slots=0,
            wait_slots=0,
            execution_progress_slots=0,
            transmission_delay_slots=None,
            evidence_source="trace",
            selected_action_available=True,
        )
        self.assertEqual(selected_action_is_illegal(unsupported)[0], True)
        self.assertEqual(selected_action_is_illegal(missing)[0], True)

    def test_report_rejects_sample_only_illegal_metrics(self) -> None:
        with patch("src.analysis.exposure_matrix_review.runner._tracked_dirty_paths", return_value=[]):
            report = build_exposure_matrix_report()
        aggregate = report.aggregate_exposure_matrix
        self.assertIsNone(aggregate["selected_illegal_action_count"])
        self.assertEqual(aggregate["selected_illegal_action_examples"], [])
        self.assertIsNone(aggregate["selected_illegal_action_rate"])
        self.assertIsNone(report.illegal_action_summary.selected_illegal_action_count)
        self.assertEqual(report.illegal_action_summary.selected_illegal_action_examples, [])
        self.assertEqual(report.illegal_action_summary.evidence_status, "unavailable")
        self.assertTrue(all(row["selected_illegal_action_count"] is None for row in report.per_strategy_seed_matrix))


if __name__ == "__main__":
    unittest.main()
