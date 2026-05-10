from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from src.analysis.structured_paper_topology_linkrate_registry import StructuredPaperTopologyLinkRateRegistryBuilder


class StructuredPaperTopologyLinkRateRegistryNoFabricationTests(unittest.TestCase):
    def test_every_recovered_item_has_evidence_or_is_unrecoverable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            paper = base / "merged.tex"
            paper.write_text(
                "FIGURE 7. Edge layer topology graph of matrix G with 20 EAs. "
                "TABLE 4. System and Learning Parameters Task Arrival Probability 0.5 "
                "Horizontal Data Rate 30 Mbps Vertical Data Rate 10 Mbps "
                "Task processing density 0.297 gigacycles/Mbit 5000 episodes 200 validation episodes "
                "gamma=[0.2,0.4,0.6,0.8,0.99]",
                encoding="utf-8",
            )
            artifact_root = base / "artifacts"
            (artifact_root / "analysis/paper-mechanism-registry").mkdir(parents=True, exist_ok=True)
            (artifact_root / "analysis/paper-figure-extraction").mkdir(parents=True, exist_ok=True)
            (artifact_root / "analysis/paper-mechanism-registry/paper-mechanism-registry.json").write_text("{}", encoding="utf-8")
            (artifact_root / "analysis/paper-figure-extraction/paper-figure-extraction.json").write_text("{}", encoding="utf-8")
            built = StructuredPaperTopologyLinkRateRegistryBuilder(paper, artifact_root, base).build()
            for registry in (built["topology"], built["parameters"]):
                for key, value in registry.items():
                    if key in {
                        "schema_version",
                        "no_fabrication_disclaimer",
                        "recovery_confidence",
                        "paper_figure_id",
                        "paper_claim_type",
                        "recovery_status",
                        "adjacency_matrix_status",
                        "source_inventory",
                        "node_count",
                        "node_ids",
                        "adjacency_matrix",
                        "legal_horizontal_destinations",
                        "edge_cloud_connectivity",
                        "source_evidence",
                        "unrecoverable_items",
                    }:
                        continue
                    if isinstance(value, dict) and value.get("recovery_status") == "recovered":
                        self.assertTrue(value["source_evidence"], key)

