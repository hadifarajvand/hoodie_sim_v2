from __future__ import annotations

import unittest

from src.analysis.load_admission_action_exposure_review.runner import run_load_admission_action_exposure_review


class LoadAdmissionActionExposureReportIntegrationTest(unittest.TestCase):
    def test_report_written(self) -> None:
        report = run_load_admission_action_exposure_review()
        payload = report.to_dict()
        self.assertTrue(payload["no_runtime_repair_performed"])
        self.assertTrue(payload["no_paper_reproduction_claim"])
        self.assertFalse(payload["metric_population_consistency_verified"])
        self.assertTrue(payload["aggregate_metrics_not_sample_derived"])
        for key in ("no_optimizer_step", "no_replay_training", "no_target_update_execution", "no_curve_fitting", "no_simulator_output_tuning"):
            self.assertTrue(payload[key])


if __name__ == "__main__":
    unittest.main()
