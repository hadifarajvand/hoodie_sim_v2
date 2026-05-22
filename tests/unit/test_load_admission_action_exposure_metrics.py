from __future__ import annotations

import unittest

from src.analysis.load_admission_action_exposure_review.runner import run_load_admission_action_exposure_review


class LoadAdmissionActionExposureMetricsTest(unittest.TestCase):
    def test_load_pressure_counts_present(self) -> None:
        payload = run_load_admission_action_exposure_review().to_dict()["load_pressure_summary"]
        for key in (
            "generated_task_count",
            "admitted_task_count",
            "terminal_task_count",
            "completed_task_count",
            "dropped_task_count",
            "pending_at_horizon_count",
            "generated_per_slot",
            "admitted_per_slot",
            "terminal_per_slot",
            "completion_rate",
            "drop_rate",
            "pending_rate",
        ):
            self.assertIn(key, payload)
        self.assertEqual(payload["generated_task_count"], 1665)
        self.assertEqual(payload["admitted_task_count"], 1665)
        self.assertEqual(payload["terminal_task_count"], 1604)
        self.assertEqual(payload["completed_task_count"], 292)
        self.assertEqual(payload["dropped_task_count"], 1312)
        self.assertEqual(payload["pending_at_horizon_count"], 61)

    def test_admission_serialization_and_action_exposure_present(self) -> None:
        payload = run_load_admission_action_exposure_review().to_dict()
        admission = payload["admission_serialization_summary"]
        action = payload["action_exposure_summary"]
        self.assertEqual(admission["same_slot_generated_count"], 1)
        self.assertEqual(admission["same_slot_admitted_count"], 5)
        self.assertEqual(action["legal_local_count"], 5)
        self.assertEqual(action["selected_local_count"], 5)
        self.assertEqual(action["selected_horizontal_count"], 0)
        self.assertEqual(action["selected_vertical_count"], 0)
        self.assertIn("legal_but_unselected_by_action", action)
        self.assertIn("queue_pressure_index", payload["queue_pressure_summary"])
        self.assertIn("transmission_delay_slots_mean", payload["offload_path_pressure_summary"])

    def test_queue_offload_and_budget_metrics(self) -> None:
        payload = run_load_admission_action_exposure_review().to_dict()
        queue = payload["queue_pressure_summary"]
        offload = payload["offload_path_pressure_summary"]
        budget = payload["budget_comparison_summary"]
        self.assertEqual(queue["private_queue_admission_count"], 0)
        self.assertEqual(queue["public_queue_admission_count"], 0)
        self.assertEqual(queue["cloud_queue_admission_count"], 0)
        self.assertEqual(offload["transmission_started_count"], 0)
        self.assertEqual(offload["offloaded_completed_count"], 0)
        self.assertEqual(budget["expected_min_compute_slots"], 2.0)
        self.assertEqual(budget["expected_transmission_slots"], 1.0)
        self.assertIn("deadline_margin_at_completion", budget)
        self.assertIn("deadline_overrun_at_drop", budget)


if __name__ == "__main__":
    unittest.main()
