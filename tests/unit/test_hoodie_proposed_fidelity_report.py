from __future__ import annotations

import unittest

from src.analysis.hoodie_proposed_fidelity.config import REQUIRED_COMPONENT_IDS
from src.analysis.hoodie_proposed_fidelity.report import build_feature_081_report, render_feature_081_report


class HoodieProposedFidelityReportTests(unittest.TestCase):
    def test_report_has_honest_matrix_and_no_rank_or_comparison_language(self) -> None:
        report = build_feature_081_report()
        self.assertTrue(report.passed)
        self.assertEqual(report.status, "hoodie_proposed_fidelity_ready")
        self.assertEqual(report.component_count, 19)
        self.assertEqual(len(report.components), 19)
        self.assertEqual(report.implemented_count, 1)
        self.assertEqual(report.partial_count, 11)
        self.assertEqual(report.missing_count, 6)
        self.assertEqual(report.not_applicable_count, 1)
        self.assertGreater(report.missing_count, 0)
        self.assertTrue(report.gap_summary)
        self.assertTrue(report.repair_plan)
        self.assertEqual({component.component_id for component in report.components}, set(REQUIRED_COMPONENT_IDS))
        rendered = render_feature_081_report(report).lower()
        self.assertNotIn("rank", rendered)
        self.assertNotIn("policy comparison", rendered)
        self.assertNotIn("proposed_dcq", rendered)
        self.assertIn("hoodie_proposed", rendered)

    def test_report_mentions_all_required_components(self) -> None:
        report = build_feature_081_report()
        component_ids = {component.component_id for component in report.components}
        self.assertEqual(len(component_ids), 19)
        self.assertIn("dqn_training", component_ids)
        self.assertIn("pubsub_recovery", component_ids)
        self.assertIn("baselines", component_ids)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
