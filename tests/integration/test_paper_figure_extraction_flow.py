from __future__ import annotations

from hashlib import sha256
import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.paper_figure_extraction import PaperFigureExtractor


def _digest(path: Path) -> str:
    h = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


class PaperFigureExtractionFlowTests(unittest.TestCase):
    def test_real_paper_baseline_extraction_flow(self) -> None:
        paper = Path("resources/papers/hoodie/ocr/merged.tex")
        root = Path("artifacts/campaigns/paper-baseline-reproduction")
        watched = [
            paper,
            root / "campaign" / "campaign-summary.json",
            root / "campaign" / "policy-summary.json",
            root / "campaign" / "scenario-summary.json",
            root / "matrix" / "matrix-summary.csv",
        ]
        before = {path: _digest(path) for path in watched}

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "out"
            extractor = PaperFigureExtractor(paper, root, output_dir)
            first = extractor.write_outputs()
            second = extractor.write_outputs()

            self.assertEqual(_digest(first["paper-figure-extraction.json"]), _digest(second["paper-figure-extraction.json"]))
            self.assertEqual(_digest(first["paper-figure-extraction.md"]), _digest(second["paper-figure-extraction.md"]))

            payload = json.loads(first["paper-figure-extraction.json"].read_text(encoding="utf-8"))
            entries = {entry["figure_id"]: entry for entry in payload["figure_entries"]}
            self.assertEqual(set(entries), {"Figure 7", "Figure 8", "Figure 9", "Figure 10", "Figure 11"})
            self.assertTrue(all(entry["paper_ocr_evidence"] for entry in entries.values()))
            self.assertEqual(entries["Figure 8"]["support_status"], "unsupported")
            self.assertEqual(entries["Figure 11"]["support_status"], "unsupported")
            self.assertIn(entries["Figure 10"]["support_status"], {"partially_supported", "supported"})
            self.assertTrue(entries["Figure 10"]["extracted_artifact_metrics"]["per_run"])
            self.assertEqual(entries["Figure 9"]["support_status"], "partially_supported")
            self.assertTrue(entries["Figure 9"]["extracted_artifact_metrics"]["action_distribution_by_policy"])
            self.assertFalse(payload["comparison_readiness"]["full_paper_comparison_ready"])
            self.assertIn("Current baseline artifacts do not contain true HOODIE DRL training curves.", payload["global_warnings"])
            self.assertTrue((output_dir / "paper-figure-extraction.json").exists())
            self.assertTrue((output_dir / "paper-figure-extraction.md").exists())

        after = {path: _digest(path) for path in watched}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
