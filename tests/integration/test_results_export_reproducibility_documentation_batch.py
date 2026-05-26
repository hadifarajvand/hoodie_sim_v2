from __future__ import annotations

import json
import unittest

from src.analysis.results_export_reproducibility_documentation_batch import generate_results_export_reproducibility_documentation_batch_artifacts
from src.analysis.results_export_reproducibility_documentation_batch.config import (
    FINAL_ARTIFACT_INDEX_JSON,
    FINAL_INTEGRITY_AUDIT_JSON,
    FINAL_MECHANISM_DOC_MD,
    FIGURE_DATA_JSON,
    REPRODUCIBILITY_PACKAGE_MD,
    RESULTS_TABLE_CSV,
    RESULTS_TABLE_MD,
)


class ResultsExportReproducibilityDocumentationBatchIntegrationTests(unittest.TestCase):
    def test_artifacts_are_written(self) -> None:
        report, json_path, md_path = generate_results_export_reproducibility_documentation_batch_artifacts()
        self.assertTrue(json_path.exists())
        self.assertTrue(md_path.exists())
        for path in [FINAL_INTEGRITY_AUDIT_JSON, RESULTS_TABLE_CSV, RESULTS_TABLE_MD, FIGURE_DATA_JSON, REPRODUCIBILITY_PACKAGE_MD, FINAL_MECHANISM_DOC_MD, FINAL_ARTIFACT_INDEX_JSON]:
            self.assertTrue(path.exists())
        self.assertEqual(json.loads(json_path.read_text(encoding="utf-8")), report.to_dict())


if __name__ == "__main__":
    unittest.main()
