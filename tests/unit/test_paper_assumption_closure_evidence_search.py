from __future__ import annotations

import unittest

from src.analysis.paper_assumption_closure_evidence_exhaustion.report import build_assumption_closure_report


class PaperAssumptionClosureEvidenceSearchTests(unittest.TestCase):
    def test_classification_vocabulary_is_used(self) -> None:
        report = build_assumption_closure_report()
        allowed = {
            "recovered",
            "partially_recovered",
            "contradicted",
            "assumption_backed_requires_user_approval",
            "unrecoverable_after_evidence_exhaustion",
            "out_of_scope",
        }
        for item in report.items:
            self.assertIn(item.status, allowed)

    def test_evidence_snippets_are_item_specific(self) -> None:
        report = build_assumption_closure_report()
        for item in report.items:
            for evidence in item.positive_evidence + item.negative_evidence:
                self.assertLessEqual(len(evidence.raw_evidence), 400)
                self.assertTrue(evidence.raw_evidence.strip())
                self.assertNotIn("page 1", evidence.raw_evidence.lower())
                self.assertNotIn("page-1", evidence.raw_evidence.lower())
                self.assertFalse(evidence.raw_evidence.startswith("Searched for"))

    def test_negative_evidence_is_not_search_failure_landfill(self) -> None:
        report = build_assumption_closure_report()
        for item in report.items:
            for evidence in item.negative_evidence:
                self.assertNotIn("Searched for", evidence.raw_evidence)
                self.assertNotIn("item-specific value not recovered", evidence.raw_evidence)
                self.assertNotIn("/ocr/merged", evidence.source_reference)
                self.assertFalse(evidence.source_reference.endswith("HOODIE_paper.pdf"))
            if item.status == "unrecoverable_after_evidence_exhaustion":
                self.assertTrue(item.searched_sources)
                self.assertLessEqual(len(item.negative_evidence), len(item.searched_sources))
                for search in item.searched_sources:
                    self.assertIn("match_count", search)
                    self.assertIn("relevant_match_count", search)
                    self.assertIsInstance(search["search_terms"], list)

    def test_negative_evidence_is_structured_only(self) -> None:
        report = build_assumption_closure_report()
        for item in report.items:
            for evidence in item.negative_evidence:
                self.assertNotIn("caption", evidence.raw_evidence.lower())
                self.assertIn("prior_registry_or_report_statement", evidence.source_type)
