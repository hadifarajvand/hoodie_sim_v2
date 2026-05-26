from __future__ import annotations

import unittest

from src.analysis.results_export_reproducibility_documentation_batch import build_results_export_reproducibility_documentation_batch_report


class ResultsExportReproducibilityDocumentationBatchBehaviorEquivalenceTests(unittest.TestCase):
    def test_documentation_and_exports_share_source_artifact_model(self) -> None:
        payload = build_results_export_reproducibility_documentation_batch_report().to_dict()
        source_artifacts = payload["reproducibility_package_summary"]["source_artifacts"]
        index_entries = payload["artifact_index_summary"]["artifact_entries"]
        self.assertTrue(source_artifacts)
        self.assertTrue(index_entries)
        self.assertEqual(payload["claim_boundary_summary"]["controlled_experiment_data"], True)

    def test_behavior_equivalence_check_names_are_unique(self) -> None:
        payload = build_results_export_reproducibility_documentation_batch_report().to_dict()
        names = [entry["name"] for entry in payload["prerequisite_tags_verified"]]
        self.assertEqual(len(names), len(set(names)))


if __name__ == "__main__":
    unittest.main()
