from __future__ import annotations

import unittest

from src.analysis.exposure_matrix_paper_mechanism_rerun_with_outcome_evidence import build_exposure_matrix_paper_mechanism_rerun_report


class ExposureMatrixPaperMechanismRerunBehaviorEquivalenceTests(unittest.TestCase):
    def test_behavior_equivalence_checks_unique_and_passed(self) -> None:
        payload = build_exposure_matrix_paper_mechanism_rerun_report().to_dict()
        checks = payload["behavior_equivalence_summary"]["checks"]
        names = [check["name"] for check in checks]
        self.assertEqual(len(names), len(set(names)))
        self.assertTrue(payload["behavior_equivalence_passed"])
        self.assertTrue(payload["behavior_equivalence_summary"]["passed"])


if __name__ == "__main__":
    unittest.main()
