from __future__ import annotations

import unittest

from src.analysis.paper_assumption_closure_evidence_exhaustion.report import build_assumption_closure_report


class PaperAssumptionClosureDeterminismTests(unittest.TestCase):
    def test_report_generation_is_deterministic(self) -> None:
        first = build_assumption_closure_report().to_dict()
        second = build_assumption_closure_report().to_dict()
        self.assertEqual(first, second)

