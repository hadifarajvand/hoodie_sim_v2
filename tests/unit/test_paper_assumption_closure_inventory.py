from __future__ import annotations

import unittest

from src.analysis.paper_assumption_closure_evidence_exhaustion.report import build_assumption_closure_report


class PaperAssumptionClosureInventoryTests(unittest.TestCase):
    def test_inventory_contains_known_high_risk_items(self) -> None:
        report = build_assumption_closure_report()
        item_ids = {item.item_id for item in report.items}
        expected = {
            "Figure_7_adjacency",
            "legal_horizontal_destinations",
            "EA_private_cpu_capacity",
            "EA_public_cpu_capacity",
            "cloud_cpu_capacity",
            "cloud_data_rate",
            "timeout_value",
            "multi_agent_aggregation_reduction_order",
            "Phi_n_pub_exact_formatting",
        }
        self.assertTrue(expected.issubset(item_ids))

