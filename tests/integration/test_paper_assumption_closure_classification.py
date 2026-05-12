from __future__ import annotations

import unittest

from src.analysis.paper_assumption_closure_evidence_exhaustion.report import build_assumption_closure_report


class PaperAssumptionClosureClassificationTests(unittest.TestCase):
    def test_every_item_receives_exactly_one_final_status(self) -> None:
        report = build_assumption_closure_report()
        self.assertEqual(len(report.items), report.inventory_summary.total_items)
        for item in report.items:
            self.assertTrue(item.status)

