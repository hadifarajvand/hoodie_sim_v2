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
            self.assertTrue(item.searched_sources)
            for search in item.searched_sources:
                self.assertIn("search_terms", search)
                self.assertIn("match_count", search)
                self.assertIn("relevant_match_count", search)
        for item in assumption_items:
            self.assertTrue(item.runtime_approval_required)
            self.assertTrue(item.evidence_exhaustion_rationale)
            self.assertTrue(getattr(item, "proposed_assumption_rule", "") or getattr(item, "proposed_value", ""))

    def test_figure7_is_unrecoverable_without_edge_evidence(self) -> None:
        report = build_assumption_closure_report()
        figure7 = next(item for item in report.items if item.item_id == "Figure_7_adjacency")
        self.assertEqual(figure7.status, "unrecoverable_after_evidence_exhaustion")
        self.assertTrue(figure7.evidence_exhaustion_rationale)
        self.assertFalse(figure7.runtime_approval_required)
        self.assertTrue(figure7.searched_sources)
        for evidence in figure7.negative_evidence:
            self.assertNotIn("/ocr/merged", evidence.source_reference)
            self.assertFalse(evidence.source_reference.endswith("HOODIE_paper.pdf"))

    def test_runtime_affecting_items_without_proposed_rules_are_unrecoverable(self) -> None:
        report = build_assumption_closure_report()
        targets = {
            "legal_horizontal_destinations",
            "EA_private_cpu_capacity",
            "EA_public_cpu_capacity",
            "cloud_cpu_capacity",
            "cloud_data_rate",
            "timeout_value",
        }
        for item in report.items:
            if item.item_id in targets:
                self.assertEqual(item.status, "unrecoverable_after_evidence_exhaustion")
                self.assertTrue(item.evidence_exhaustion_rationale)
                self.assertTrue(item.searched_sources)
                for evidence in item.negative_evidence:
                    self.assertNotIn("/ocr/merged", evidence.source_reference)
                    self.assertFalse(evidence.source_reference.endswith("HOODIE_paper.pdf"))
