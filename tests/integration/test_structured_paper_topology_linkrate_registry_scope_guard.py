from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.analysis.structured_paper_topology_linkrate_registry import StructuredPaperTopologyLinkRateRegistryBuilder


class StructuredPaperTopologyLinkRateRegistryScopeGuardTests(unittest.TestCase):
    def test_source_files_are_not_mutated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            paper = base / "merged.tex"
            paper.write_text("FIGURE 7. Edge layer topology graph of matrix G with 20 EAs. TABLE 4. System and Learning Parameters Task Arrival Probability 0.5 Horizontal Data Rate 30 Mbps Vertical Data Rate 10 Mbps Task processing density 0.297 gigacycles/Mbit 5000 episodes 200 validation episodes gamma=[0.2,0.4,0.6,0.8,0.99]", encoding="utf-8")
            art = base / "artifacts"
            (art / "analysis/paper-mechanism-registry").mkdir(parents=True, exist_ok=True)
            (art / "analysis/paper-figure-extraction").mkdir(parents=True, exist_ok=True)
            (art / "analysis/paper-mechanism-registry/paper-mechanism-registry.json").write_text("{}", encoding="utf-8")
            (art / "analysis/paper-figure-extraction/paper-figure-extraction.json").write_text("{}", encoding="utf-8")
            watched = [paper]
            before = {p: p.read_text(encoding="utf-8") for p in watched}
            StructuredPaperTopologyLinkRateRegistryBuilder(paper, art, base).write_outputs()
            after = {p: p.read_text(encoding="utf-8") for p in watched}
            self.assertEqual(before, after)

