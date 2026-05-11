from __future__ import annotations

import unittest

from src.analysis.link_rate_transmission_delay_contract.report import build_link_rate_contract_report
from src.analysis.structured_paper_topology_linkrate_registry import StructuredPaperTopologyLinkRateRegistryBuilder
from pathlib import Path
import tempfile


class LinkRateTopologyFabricationGuardTest(unittest.TestCase):
    def test_report_marks_figure_7_and_horizontal_destinations_unrecoverable(self) -> None:
        report = build_link_rate_contract_report().to_dict()
        self.assertEqual(report["topology_boundaries"]["figure_7_adjacency_status"], "unrecoverable")
        self.assertEqual(report["topology_boundaries"]["legal_horizontal_destinations_status"], "non-paper-backed")
        self.assertFalse(report["topology_boundaries"]["paper_topology_injected"])
        self.assertEqual(report["link_rate_controls"]["per_edge_control_status"], "unsupported_without_non_fabricated_evidence")

    def test_recovered_topology_registry_does_not_invent_edges(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            paper = base / "merged.tex"
            paper.write_text("FIGURE 7. Edge layer topology graph of matrix G with 20 EAs. TABLE 4. System and Learning Parameters Task Arrival Probability 0.5 Horizontal Data Rate 30 Mbps Vertical Data Rate 10 Mbps Task processing density 0.297 gigacycles/Mbit 5000 episodes 200 validation episodes gamma=[0.2,0.4,0.6,0.8,0.99]", encoding="utf-8")
            art = base / "artifacts"
            (art / "analysis/paper-mechanism-registry").mkdir(parents=True, exist_ok=True)
            (art / "analysis/paper-figure-extraction").mkdir(parents=True, exist_ok=True)
            (art / "analysis/paper-mechanism-registry/paper-mechanism-registry.json").write_text("{}", encoding="utf-8")
            (art / "analysis/paper-figure-extraction/paper-figure-extraction.json").write_text("{}", encoding="utf-8")
            topology = StructuredPaperTopologyLinkRateRegistryBuilder(paper, art, base).build()["topology"]
            self.assertEqual(topology["adjacency_matrix_status"], "unrecoverable")
            self.assertIsNone(topology["adjacency_matrix"])
            self.assertTrue(topology["no_fabrication_disclaimer"])


if __name__ == "__main__":
    unittest.main()
