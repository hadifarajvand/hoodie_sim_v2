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
