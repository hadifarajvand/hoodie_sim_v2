from __future__ import annotations

import unittest

from src.analysis.load_admission_action_exposure_review.runner import run_load_admission_action_exposure_review


class LoadAdmissionActionExposureReportIntegrationTest(unittest.TestCase):
    def test_report_written(self) -> None:
        report = run_load_admission_action_exposure_review()
        payload = report.to_dict()
        self.assertTrue(payload["no_runtime_repair_performed"])
        self.assertTrue(payload["no_paper_reproduction_claim"])


if __name__ == "__main__":
    unittest.main()
