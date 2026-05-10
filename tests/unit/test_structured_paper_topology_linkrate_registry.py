from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from src.analysis.structured_paper_topology_linkrate_registry import StructuredPaperTopologyLinkRateRegistryBuilder


class StructuredPaperTopologyLinkRateRegistryUnitTests(unittest.TestCase):
    def _fixture(self, base: Path) -> tuple[Path, Path]:
        paper = base / "merged.tex"
        paper.write_text(
            "\n".join(
                [
                    "FIGURE 7. Edge layer topology graph of matrix G with 20 EAs.",
                    "TABLE 4. System and Learning Parameters",
                    "<tr><td>Task Arrival Probability</td><td>$\\mathcal{P}$</td><td>0.5</td></tr>",
                    "<tr><td>Horizontal Data Rate</td><td>$R_{H}$</td><td>30 Mbps [23]</td></tr>",
                    "<tr><td>Vertical Data Rate</td><td>$R_{V}$</td><td>10 Mbps</td></tr>",
                    "<tr><td>Task size</td><td>$\\eta_{n}(t)$</td><td>[2,2.1,...,5] Mbits</td></tr>",
                    "<tr><td>Task processing density</td><td>$\\rho_{n}(t)$</td><td>0.297 gigacycles/Mbit [39]</td></tr>",
                    "<tr><td>Number of EAs</td><td>$N$</td><td>20</td></tr>",
                    "5000 episodes and 200 validation episodes",
                    "gamma=[0.2,0.4,0.6,0.8,0.99]",
                    "learning rate $\\alpha_{lr}$ = [10^{-9},5\\cdot10^{-9},10^{-8},10^{-7},5\\cdot10^{-7},7\\cdot10^{-7}]",
                ]
            ),
            encoding="utf-8",
        )
        artifact_root = base / "artifacts"
        (artifact_root / "analysis/paper-mechanism-registry").mkdir(parents=True, exist_ok=True)
        (artifact_root / "analysis/paper-figure-extraction").mkdir(parents=True, exist_ok=True)
        (artifact_root / "analysis/paper-mechanism-registry/paper-mechanism-registry.json").write_text("{}", encoding="utf-8")
        (artifact_root / "analysis/paper-figure-extraction/paper-figure-extraction.json").write_text("{}", encoding="utf-8")
        return paper, artifact_root

    def test_source_gates_and_schema_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paper, artifact_root = self._fixture(Path(tmp))
            builder = StructuredPaperTopologyLinkRateRegistryBuilder(paper, artifact_root, Path(tmp))
            out = builder.build()
            self.assertIn("schema_version", out["topology"])
            self.assertIn("schema_version", out["parameters"])
            self.assertEqual(out["topology"]["paper_figure_id"], "Figure 7")
            self.assertTrue(out["topology"]["no_fabrication_disclaimer"])
            self.assertTrue(out["parameters"]["no_fabrication_disclaimer"])

    def test_topology_is_marked_unrecoverable_without_fabricated_edges(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paper, artifact_root = self._fixture(Path(tmp))
            topology = StructuredPaperTopologyLinkRateRegistryBuilder(paper, artifact_root, Path(tmp)).build()["topology"]
            self.assertEqual(topology["adjacency_matrix_status"], "unrecoverable")
            self.assertIsNone(topology["adjacency_matrix"])
            self.assertIn("topology_adjacency_edges", topology["unrecoverable_items"])

    def test_parameter_registry_has_recovery_status_and_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paper, artifact_root = self._fixture(Path(tmp))
            params = StructuredPaperTopologyLinkRateRegistryBuilder(paper, artifact_root, Path(tmp)).build()["parameters"]
            self.assertEqual(params["task_arrival_parameters"]["recovery_status"], "recovered")
            self.assertTrue(params["task_arrival_parameters"]["source_evidence"])
            self.assertEqual(params["cpu_capacities"]["EA_private"]["recovery_status"], "unrecoverable")
            self.assertEqual(params["scenario_parameters"]["adjacency_matrix"]["recovery_status"], "unrecoverable")

    def test_written_artifacts_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paper, artifact_root = self._fixture(Path(tmp))
            builder = StructuredPaperTopologyLinkRateRegistryBuilder(paper, artifact_root, Path(tmp))
            first = builder.write_outputs()
            first_bytes = {k: p.read_bytes() for k, p in first.items()}
            second = builder.write_outputs()
            second_bytes = {k: p.read_bytes() for k, p in second.items()}
            self.assertEqual(first_bytes, second_bytes)

    def test_scope_guard_does_not_mutate_source_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paper, artifact_root = self._fixture(Path(tmp))
            before = paper.read_text(encoding="utf-8")
            StructuredPaperTopologyLinkRateRegistryBuilder(paper, artifact_root, Path(tmp)).write_outputs()
            after = paper.read_text(encoding="utf-8")
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
