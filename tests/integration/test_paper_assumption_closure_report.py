from __future__ import annotations

import json
import unittest

from src.analysis.paper_assumption_closure_evidence_exhaustion.report import build_assumption_closure_report, write_assumption_closure_report


class PaperAssumptionClosureReportTests(unittest.TestCase):
    def test_report_schema_and_json_parse(self) -> None:
        report = build_assumption_closure_report()
        json_path, markdown_path = write_assumption_closure_report(report)
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        for key in (
            "feature_id",
            "schema_version",
            "source_gates",
            "inventory_summary",
            "items",
            "recovered_items",
            "partially_recovered_items",
            "contradicted_items",
            "assumption_backed_items",
            "unrecoverable_after_evidence_exhaustion_items",
            "out_of_scope_items",
            "manual_review_required_items",
            "runtime_dependency_decisions",
            "no_training_or_policy_drift",
            "no_dependency_drift",
            "final_verdict",
        ):
            self.assertIn(key, payload)
        self.assertTrue(markdown_path.exists())
        for item in payload["items"]:
            self.assertNotIn("unknown", item["item_id"].lower())
            self.assertTrue(item["item_id"])
            self.assertIn("positive_evidence", item)
            self.assertIn("negative_evidence", item)
            self.assertIn("searched_sources", item)
            for evidence in item["positive_evidence"] + item["negative_evidence"]:
                self.assertTrue(evidence["raw_evidence"].strip())
                self.assertLessEqual(len(evidence["raw_evidence"]), 400)
                self.assertFalse(evidence["raw_evidence"].startswith("Searched for"))
            for search in item["searched_sources"]:
                self.assertIn("search_terms", search)
                self.assertIn("search_method", search)
                self.assertIn("match_count", search)
                self.assertIn("relevant_match_count", search)
            for evidence in item["negative_evidence"]:
                self.assertNotIn("/ocr/merged", evidence["source_reference"])
                self.assertFalse(evidence["source_reference"].endswith("HOODIE_paper.pdf"))
                self.assertIn("prior_registry_or_report_statement", evidence["source_type"])

    def test_search_failures_stay_out_of_negative_evidence(self) -> None:
        report = build_assumption_closure_report()
        for item in report.items:
            for evidence in item.negative_evidence:
                self.assertNotIn("Searched for", evidence.raw_evidence)
                self.assertNotIn("item-specific value not recovered", evidence.raw_evidence)
