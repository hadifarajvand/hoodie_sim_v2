from __future__ import annotations

import unittest

from src.analysis.paper_assumption_closure_evidence_exhaustion.report import build_assumption_closure_report


class PaperAssumptionClosureCompletenessTests(unittest.TestCase):
    def test_unrecoverable_items_include_rationale_and_assumption_items_require_approval(self) -> None:
        report = build_assumption_closure_report()
        unrecoverable = [item for item in report.items if item.status == "unrecoverable_after_evidence_exhaustion"]
        assumption_items = [item for item in report.items if item.status == "assumption_backed_requires_user_approval"]
        for item in unrecoverable:
            self.assertTrue(item.evidence_exhaustion_rationale)
        for item in assumption_items:
            self.assertTrue(item.runtime_approval_required)

