from __future__ import annotations

import unittest

from src.analysis.load_admission_action_exposure_review.runner import run_load_admission_action_exposure_review


class LoadAdmissionActionExposureSchemaTest(unittest.TestCase):
    def test_report_schema_and_verdict(self) -> None:
        report = run_load_admission_action_exposure_review()
        payload = report.to_dict()
        self.assertEqual(payload["feature_id"], "046-load-admission-action-exposure-review")
        self.assertEqual(payload["final_verdict"], "mixed_load_action_pressure_explains_completion_weakness")
        self.assertEqual(payload["recommended_next_feature"], "Feature 047 — Paper HOODIE Observation Vector")
        for key in (
            "load_pressure_summary",
            "admission_serialization_summary",
            "action_exposure_summary",
            "queue_pressure_summary",
            "offload_path_pressure_summary",
            "budget_comparison_summary",
        ):
            self.assertIn(key, payload)

    def test_includes_passive_inputs(self) -> None:
        report = run_load_admission_action_exposure_review()
        sources = report.to_dict()["trace_input_sources"]
        self.assertTrue(any(item["feature"] == "044" for item in sources))
        self.assertTrue(any(item["feature"] == "045" for item in sources))


if __name__ == "__main__":
    unittest.main()
