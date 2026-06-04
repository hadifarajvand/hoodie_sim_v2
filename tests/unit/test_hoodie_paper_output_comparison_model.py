from __future__ import annotations

import unittest

from src.analysis.hoodie_paper_output_comparison.config import ACTIVE_POLICIES, ALLOWED_PAPER_COMPARISON_METRICS
from src.analysis.hoodie_paper_output_comparison.runner import (
    build_metric_alignment_rows,
    build_paper_output_extraction,
    build_report,
    build_ranking_agreement_rows,
)


class HoodiePaperOutputComparisonModelTests(unittest.TestCase):
    def test_paper_extraction_schema(self) -> None:
        items = build_paper_output_extraction()
        self.assertGreater(len(items), 0)
        item = items[0]
        self.assertTrue(item.paper_item_id)
        self.assertTrue(item.source_location)
        self.assertTrue(item.item_type)
        self.assertTrue(item.value_extraction_method)
        self.assertTrue(item.extraction_confidence)
        self.assertIsInstance(item.to_dict()["policies"], list)

    def test_metric_alignment_schema_and_metrics(self) -> None:
        rows = build_metric_alignment_rows()
        metrics = {row.paper_metric for row in rows}
        self.assertEqual(metrics, set(ALLOWED_PAPER_COMPARISON_METRICS) | {
            "timeout_drop_rate",
            "unavailable_drop_rate",
            "deadline_violation_rate",
            "queue_stability_score",
            "illegal_action_rejection_count",
        })
        self.assertTrue(all(row.caveat for row in rows))

    def test_report_boundary_and_verdict(self) -> None:
        report = build_report()
        self.assertEqual(report.feature_id, "087-hoodie-paper-output-comparison")
        self.assertIn(report.verdict, {"paper_output_comparison_ready", "paper_output_comparison_partial", "paper_output_comparison_blocked"})
        self.assertTrue(report.feature_086_boundary)
        self.assertEqual(tuple(ACTIVE_POLICIES), ("HOODIE", "RO", "FLC", "VO", "HO", "BCO", "MLEO"))
        self.assertGreater(report.paper_items_extracted, 0)
        self.assertGreater(report.paper_items_comparable, 0)

    def test_ranking_agreement_rows_cover_allowed_metrics(self) -> None:
        rows = build_ranking_agreement_rows()
        self.assertEqual({row.metric for row in rows}, set(ALLOWED_PAPER_COMPARISON_METRICS))
        self.assertTrue(any(row.agreement_level == "partial" for row in rows))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

