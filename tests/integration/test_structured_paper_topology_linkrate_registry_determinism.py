from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from src.analysis.structured_paper_topology_linkrate_registry import StructuredPaperTopologyLinkRateRegistryBuilder


class StructuredPaperTopologyLinkRateRegistryDeterminismTests(unittest.TestCase):
    def _fixture(self, base: Path) -> tuple[Path, Path]:
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
        return paper, artifact_root

    def test_stable_registry_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paper, artifact_root = self._fixture(Path(tmp))
            builder = StructuredPaperTopologyLinkRateRegistryBuilder(paper, artifact_root, Path(tmp))
            first = builder.write_outputs()
            first_text = {k: p.read_text(encoding="utf-8") for k, p in first.items()}
            second = builder.write_outputs()
            second_text = {k: p.read_text(encoding="utf-8") for k, p in second.items()}
            self.assertEqual(first_text, second_text)

