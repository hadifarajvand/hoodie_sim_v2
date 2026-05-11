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

