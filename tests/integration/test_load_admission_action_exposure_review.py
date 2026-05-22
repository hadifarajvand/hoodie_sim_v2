from __future__ import annotations

import unittest

from src.analysis.load_admission_action_exposure_review.runner import run_load_admission_action_exposure_review


class LoadAdmissionActionExposureReviewIntegrationTest(unittest.TestCase):
    def test_review_routes_to_feature_047(self) -> None:
        payload = run_load_admission_action_exposure_review().to_dict()
        dominant_sources = payload["dominant_pressure_sources"]
        self.assertEqual(payload["recommended_next_feature"], "exposure-matrix review")
        self.assertEqual(payload["final_verdict"], "load_pressure_explains_completion_weakness")
        self.assertEqual(dominant_sources[0]["source"], "load_pressure")
        self.assertEqual(dominant_sources[0]["rank"], 1)
        self.assertEqual(dominant_sources[1]["source"], "admission_serialization")
        self.assertNotEqual(payload["recommended_next_feature"], "runtime repair")

    def test_runtime_repair_not_recommended_from_ordinary_pressure(self) -> None:
        payload = run_load_admission_action_exposure_review().to_dict()
        self.assertTrue(payload["no_runtime_repair_performed"])
        self.assertNotEqual(payload["recommended_next_feature"], "runtime repair")


if __name__ == "__main__":
    unittest.main()
