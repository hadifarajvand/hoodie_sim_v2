from __future__ import annotations

import unittest

from src.analysis.load_admission_action_exposure_review.runner import run_load_admission_action_exposure_review


class LoadAdmissionActionExposureMetricsTest(unittest.TestCase):
    def test_load_pressure_counts_present(self) -> None:
        payload = run_load_admission_action_exposure_review().to_dict()["load_pressure_summary"]
        self.assertEqual(payload["evidence_population"], "feature_045_full_reconstruction_summary")
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
        self.assertEqual(admission["evidence_population"], "unavailable_in_committed_artifacts")
        self.assertIsNone(admission["same_slot_generated_count"])
        self.assertIsNone(admission["same_slot_admitted_count"])
        self.assertIsNone(action["legal_local_count"])
        self.assertIsNone(action["legal_horizontal_count"])
        self.assertIsNone(action["legal_vertical_count"])
        self.assertIsNone(action["selected_local_count"])
        self.assertIsNone(action["selected_horizontal_count"])
        self.assertIsNone(action["selected_vertical_count"])
        self.assertIn("legal_but_unselected_by_action", action)
        self.assertIsNone(action["legal_but_unselected_by_action"]["local"])
        self.assertEqual(payload["queue_pressure_summary"]["evidence_population"], "unavailable_in_committed_artifacts")
        self.assertEqual(payload["offload_path_pressure_summary"]["evidence_population"], "unavailable_in_committed_artifacts")

    def test_queue_offload_and_budget_metrics(self) -> None:
        payload = run_load_admission_action_exposure_review().to_dict()
        queue = payload["queue_pressure_summary"]
        offload = payload["offload_path_pressure_summary"]
        budget = payload["budget_comparison_summary"]
        self.assertIsNone(queue["private_queue_admission_count"])
        self.assertIsNone(queue["public_queue_admission_count"])
        self.assertIsNone(queue["cloud_queue_admission_count"])
        self.assertIsNone(offload["transmission_started_count"])
        self.assertIsNone(offload["offloaded_completed_count"])
        self.assertEqual(budget["evidence_population"], "representative_trace_sample")
        self.assertEqual(
            budget["representative_task_ids"],
            [
                "environment_default_policy_probe:0:1",
                "environment_default_policy_probe:0:2",
                "environment_default_policy_probe:0:3",
                "environment_default_policy_probe:0:4",
                "environment_default_policy_probe:0:5",
            ],
        )
        self.assertIn("representative_examples", budget)
        self.assertEqual(budget["expected_min_compute_slots"], None)
        self.assertEqual(budget["expected_transmission_slots"], None)


if __name__ == "__main__":
    unittest.main()
