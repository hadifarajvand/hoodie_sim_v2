from __future__ import annotations

import unittest

from src.analysis.smoke_training import SmokeTrainingConfig, run_smoke_training


class SmokeTrainingDeterminismIntegrationTests(unittest.TestCase):
    def test_smoke_training_is_deterministic_for_same_seed(self) -> None:
        report_one = run_smoke_training(SmokeTrainingConfig())
        report_two = run_smoke_training(SmokeTrainingConfig())
        self.assertEqual(report_one.to_dict(), report_two.to_dict())
        self.assertTrue(report_one.deterministic_repeatability_verified["same_seed_match"])


if __name__ == "__main__":
    unittest.main()
