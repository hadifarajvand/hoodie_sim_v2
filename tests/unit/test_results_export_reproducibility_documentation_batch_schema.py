from __future__ import annotations

import unittest

from src.analysis.results_export_reproducibility_documentation_batch import build_results_export_reproducibility_documentation_batch_report
from src.analysis.results_export_reproducibility_documentation_batch.config import FEATURE_ID, REQUIRED_TOP_LEVEL_FIELDS
from src.analysis.results_export_reproducibility_documentation_batch.model import ResultsExportReproducibilityDocumentationBatchReport


class ResultsExportReproducibilityDocumentationBatchSchemaTests(unittest.TestCase):
    def test_report_has_required_fields_and_pass_verdict(self) -> None:
        payload = build_results_export_reproducibility_documentation_batch_report().to_dict()
        for key in REQUIRED_TOP_LEVEL_FIELDS:
            self.assertIn(key, payload)
        self.assertEqual(payload["feature_id"], FEATURE_ID)
        self.assertEqual(payload["final_verdict"], "results_export_reproducibility_documentation_batch_passed")
        self.assertEqual(payload["remaining_blockers"], [])

    def test_pass_with_blockers_is_rejected(self) -> None:
        payload = build_results_export_reproducibility_documentation_batch_report().to_dict()
        payload["remaining_blockers"] = ["feature_062_prerequisite_blocked"]
        payload["final_verdict"] = "results_export_reproducibility_documentation_batch_passed"
        with self.assertRaises(ValueError):
            ResultsExportReproducibilityDocumentationBatchReport(**payload)


if __name__ == "__main__":
    unittest.main()
