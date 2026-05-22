from __future__ import annotations

import unittest

from src.analysis.load_admission_action_exposure_review.runner import run_load_admission_action_exposure_review


class LoadAdmissionActionExposureMetricsTest(unittest.TestCase):
    def test_load_pressure_counts_present(self) -> None:
        payload = run_load_admission_action_exposure_review().to_dict()["load_pressure_summary"]
        for key in ("generated_task_count", "admitted_task_count", "terminal_task_count", "completed_task_count", "dropped_task_count", "pending_at_horizon_count"):
            self.assertIn(key, payload)

    def test_action_and_queue_metrics_present(self) -> None:
        payload = run_load_admission_action_exposure_review().to_dict()
        self.assertIn("legal_but_unselected_by_action", payload["action_exposure_summary"])
        self.assertIn("queue_pressure_index", payload["queue_pressure_summary"])
        self.assertIn("transmission_delay_slots_mean", payload["offload_path_pressure_summary"])


if __name__ == "__main__":
    unittest.main()
