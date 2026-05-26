from __future__ import annotations

import unittest

from src.analysis.results_export_reproducibility_documentation_batch import build_results_export_reproducibility_documentation_batch_report


class ResultsExportReproducibilityDocumentationBatchMetricsTests(unittest.TestCase):
    def test_export_claims_map_to_sources_and_unsupported_claims_remain_unsupported(self) -> None:
        payload = build_results_export_reproducibility_documentation_batch_report().to_dict()
        audit = payload["final_integrity_audit_summary"]
        self.assertTrue(audit["source_mapping_complete"])
        unsupported = {claim["claim"] for claim in audit["claim_mappings"] if claim["status"] == "unsupported"}
        self.assertIn("paper reproduction", unsupported)
        self.assertIn("unsupported superiority", unsupported)

    def test_results_table_and_figure_exports_retain_not_claimed_metrics(self) -> None:
        payload = build_results_export_reproducibility_documentation_batch_report().to_dict()
        rows = payload["results_export_summary"]["table_rows"]
        self.assertTrue(any(row["value_status"] == "not_claimed" for row in rows))
        self.assertTrue(payload["results_export_summary"]["controlled_experiment_data_only"])
        self.assertTrue(payload["results_export_summary"]["figure_data"]["no_invented_values"])


if __name__ == "__main__":
    unittest.main()
