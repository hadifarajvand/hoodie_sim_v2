from __future__ import annotations

from hashlib import sha256
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


class PaperFigureExtractionTests(unittest.TestCase):
    def _fixture(self, base: Path) -> tuple[Path, Path]:
        paper_path = base / "merged.tex"
        paper_path.write_text(
            "\n".join(
                [
                    "FIGURE 7. Edge layer topology graph of matrix G with 20 EAs.",
                    "FIGURE 8. Accumulated reward time-course averaged across agents for learning rate and discount factor.",
                    "Fig. 9b depicts the distribution of actions taken by HOODIE agents across task arrival probabilities.",
                    "Fig. 10a presents average delay and Fig. 10d illustrates drop ratio across offloading schemes.",
                    "FIGURE 11. Average task delay of HOODIE with vs without the LSTM inclusion as a function of training episodes.",
                ]
            ),
            encoding="utf-8",
        )
        root = base / "campaign"
        (root / "campaign").mkdir(parents=True, exist_ok=True)
        (root / "matrix" / "traces").mkdir(parents=True, exist_ok=True)
        (root / "bundle").mkdir(parents=True, exist_ok=True)
        (root / "campaign" / "campaign-summary.json").write_text("{\"result_count\": 2, \"total_tasks\": 4}", encoding="utf-8")
        (root / "campaign" / "policy-summary.json").write_text("[]", encoding="utf-8")
        (root / "campaign" / "scenario-summary.json").write_text("[]", encoding="utf-8")
        (root / "campaign" / "determinism-check.json").write_text("{\"passed\": true}", encoding="utf-8")
        (root / "matrix" / "matrix-summary.csv").write_text(
            "policy_name,scenario_name,seed,trace_id,average_delay,drop_ratio,throughput,completed_tasks,dropped_tasks,total_tasks\n"
            "FLC,paper_default,1,paper_default-1,1.5,0.25,3,3,1,4\n"
            "VO,moderate,1,moderate-1,2.5,0.5,2,2,2,4\n",
            encoding="utf-8",
        )
        (root / "matrix" / "FLC-paper_default-1.json").write_text(
            "{\"policy_name\": \"FLC\", \"scenario_name\": \"paper_default\", \"seed\": 1, \"final_metrics\": {\"raw_records\": [{\"selected_action\": \"local\", \"terminal_outcome\": \"completed\"}, {\"selected_action\": \"local\", \"terminal_outcome\": \"dropped\"}]}}",
            encoding="utf-8",
        )
        (root / "matrix" / "VO-moderate-1.json").write_text(
            "{\"policy_name\": \"VO\", \"scenario_name\": \"moderate\", \"seed\": 1, \"final_metrics\": {\"raw_records\": [{\"selected_action\": \"vertical\", \"terminal_outcome\": \"completed\"}]}}",
            encoding="utf-8",
        )
        (root / "matrix" / "traces" / "paper_default-1.json").write_text(
            "{\"trace_id\": \"paper_default-1\", \"seed\": 1, \"metadata\": {\"scenario_name\": \"paper_default\", \"configured_arrival_probability\": \"0.5\"}, \"tasks\": [{\"arrival_slot\": 0}]}",
            encoding="utf-8",
        )
        return paper_path, root

    def test_ocr_figure_caption_extraction_from_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper, root = self._fixture(Path(tmpdir))
            report = PaperFigureExtractor(paper, root, Path(tmpdir) / "out").extract().to_dict()

            figure_ids = [entry["figure_id"] for entry in report["figure_entries"]]
            self.assertEqual(figure_ids, ["Figure 7", "Figure 8", "Figure 9", "Figure 10", "Figure 11"])
            self.assertTrue(all(entry["paper_ocr_evidence"] for entry in report["figure_entries"]))

    def test_unsupported_training_and_lstm_figures_when_artifacts_absent(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper, root = self._fixture(Path(tmpdir))
            entries = {entry["figure_id"]: entry for entry in PaperFigureExtractor(paper, root, Path(tmpdir) / "out").extract().figure_entries}

            self.assertEqual(entries["Figure 8"]["support_status"], "unsupported")
            self.assertIn("training_episode_reward_curves", entries["Figure 8"]["missing_artifacts"])
            self.assertEqual(entries["Figure 11"]["support_status"], "unsupported")
            self.assertIn("hoodie_lstm_training_delay_curve", entries["Figure 11"]["missing_artifacts"])

    def test_figure10_metrics_and_figure9_action_distribution(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper, root = self._fixture(Path(tmpdir))
            entries = {entry["figure_id"]: entry for entry in PaperFigureExtractor(paper, root, Path(tmpdir) / "out").extract().figure_entries}

            figure10 = entries["Figure 10"]
            self.assertEqual(figure10["support_status"], "partially_supported")
            self.assertEqual(len(figure10["extracted_artifact_metrics"]["per_run"]), 2)
            self.assertTrue(figure10["extracted_artifact_metrics"]["by_policy"])

            figure9 = entries["Figure 9"]
            self.assertEqual(figure9["support_status"], "partially_supported")
            self.assertTrue(figure9["extracted_artifact_metrics"]["action_distribution_by_policy"])

    def test_missing_artifact_reporting_and_deterministic_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "empty"
            root.mkdir()
            paper = Path(tmpdir) / "merged.tex"
            paper.write_text("FIGURE 7. Edge layer topology graph of matrix G with 20 EAs.", encoding="utf-8")
            extractor = PaperFigureExtractor(paper, root, Path(tmpdir) / "out")
            report = extractor.extract().to_dict()

            self.assertFalse(report["passed"])
            self.assertTrue(report["artifact_inventory"]["missing_required_files"])

            outputs = extractor.write_outputs()
            first = {_name: _digest(path) for _name, path in outputs.items()}
            outputs = extractor.write_outputs()
            second = {_name: _digest(path) for _name, path in outputs.items()}
            self.assertEqual(first, second)

    def test_input_files_are_not_mutated(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            paper, root = self._fixture(Path(tmpdir))
            watched = [paper, root / "matrix" / "matrix-summary.csv", root / "matrix" / "FLC-paper_default-1.json"]
            before = {path: _digest(path) for path in watched}
            PaperFigureExtractor(paper, root, Path(tmpdir) / "out").write_outputs()
            after = {path: _digest(path) for path in watched}
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
