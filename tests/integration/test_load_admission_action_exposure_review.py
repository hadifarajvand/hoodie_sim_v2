from __future__ import annotations

import unittest

from src.analysis.load_admission_action_exposure_review.runner import run_load_admission_action_exposure_review


class LoadAdmissionActionExposureReviewIntegrationTest(unittest.TestCase):
    def test_review_routes_to_feature_047(self) -> None:
        payload = run_load_admission_action_exposure_review().to_dict()
        self.assertEqual(payload["recommended_next_feature"], "Feature 047 — Paper HOODIE Observation Vector")
        self.assertEqual(payload["final_verdict"], "mixed_load_action_pressure_explains_completion_weakness")


if __name__ == "__main__":
    unittest.main()
