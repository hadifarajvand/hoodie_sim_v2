from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from src.analysis.paper_mechanism_registry import PaperMechanismRegistryBuilder


class PaperMechanismRegistryTests(unittest.TestCase):
    def test_tiny_ocr_fixture_creates_registry_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            paper = tmp_path / "merged.tex"
            paper.write_text(
                "FIGURE 7. Edge layer topology graph of matrix G with 20 EAs.\n"
                "Table 4 mentions Task Arrival Probability and 5000 episodes.\n"
                "The task timeout is 20 time slots and reward is negative.\n",
                encoding="utf-8",
            )
            builder = PaperMechanismRegistryBuilder(paper, tmp_path / "artifacts", tmp_path / "out")
            report = builder.build_report()
            self.assertEqual(len(report.mechanism_entries), 25)
            self.assertTrue(report.read_only)
            self.assertFalse(report.behavior_changes)
            self.assertEqual(report.registry_version, "016")
            self.assertNotEqual(report.implementation_gap_summary["implemented"], 23)
            self.assertEqual(report.implementation_gap_summary["paper_validated"], 0)
            self.assertGreater(report.implementation_gap_summary["mapped_but_unvalidated"], 0)
            self.assertGreater(report.implementation_gap_summary["partially_implemented"], 0)

    def test_missing_evidence_is_marked_missing_not_invented(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            paper = tmp_path / "merged.tex"
            paper.write_text("", encoding="utf-8")
            builder = PaperMechanismRegistryBuilder(paper, tmp_path / "artifacts", tmp_path / "out")
            report = builder.build_report()
            top = next(entry for entry in report.mechanism_entries if entry.category == "system_topology")
            self.assertTrue(top.paper_evidence)
            self.assertIn("MISSING EVIDENCE", top.paper_evidence[0].ocr_snippet)

    def test_schema_includes_evidence_status_risk_and_missing_details(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            paper = tmp_path / "merged.tex"
            paper.write_text("FIGURE 10. Average delay and drop ratio.", encoding="utf-8")
            builder = PaperMechanismRegistryBuilder(paper, tmp_path / "artifacts", tmp_path / "out")
            report = builder.build_report()
            payload = report.to_dict()
            entry = payload["mechanism_entries"][0]
            for field in ("paper_status", "implementation_status", "assumption_risk", "paper_evidence", "missing_details", "implementation_gaps", "validation_implications", "next_action"):
                self.assertIn(field, entry)

    def test_topology_adjacency_missing_is_blocking_high_risk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            paper = tmp_path / "merged.tex"
            paper.write_text("FIGURE 7. Edge layer topology graph of matrix G with 20 EAs.", encoding="utf-8")
            builder = PaperMechanismRegistryBuilder(paper, tmp_path / "artifacts", tmp_path / "out")
            report = builder.build_report()
            topology = next(entry for entry in report.mechanism_entries if entry.category == "system_topology")
            self.assertEqual(topology.assumption_risk, "blocking")
            self.assertEqual(topology.next_action, "requires_reference_kernel")
            self.assertTrue(any("adjacency" in gap["description"].lower() for gap in report.blocking_gaps))

    def test_reward_and_timeout_entries_are_high_impact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            paper = tmp_path / "merged.tex"
            paper.write_text("task timeout drop ratio reward negative", encoding="utf-8")
            builder = PaperMechanismRegistryBuilder(paper, tmp_path / "artifacts", tmp_path / "out")
            report = builder.build_report()
            reward = next(entry for entry in report.mechanism_entries if entry.category == "reward_definition")
            timeout = next(entry for entry in report.mechanism_entries if entry.category == "timeout_and_drop")
            self.assertEqual(reward.assumption_risk, "blocking")
            self.assertEqual(timeout.assumption_risk, "blocking")
            for category in (
                "system_topology",
                "horizontal_offloading",
                "link_data_rates",
                "transmission_delay",
                "computation_delay",
                "timeout_and_drop",
                "reward_definition",
                "state_representation",
                "load_forecasting_or_lstm_input",
                "dqn_double_dueling_lstm_training",
                "training_episode_protocol",
                "validation_episode_protocol",
            ):
                self.assertNotEqual(next(entry for entry in report.mechanism_entries if entry.category == category).implementation_status, "implemented")

    def test_output_ordering_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            paper = tmp_path / "merged.tex"
            paper.write_text("FIGURE 11. Average task delay of HOoDIE with vs without the LSTM inclusion as a function of the training episodes.", encoding="utf-8")
            builder = PaperMechanismRegistryBuilder(paper, tmp_path / "artifacts", tmp_path / "out")
            report1 = builder.build_report()
            report2 = builder.build_report()
            self.assertEqual([entry.category for entry in report1.mechanism_entries], [entry.category for entry in report2.mechanism_entries])
            self.assertEqual(json.dumps(report1.to_dict(), sort_keys=True), json.dumps(report2.to_dict(), sort_keys=True))

    def test_input_files_are_not_mutated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            paper = tmp_path / "merged.tex"
            paper.write_text("FIGURE 8. Accumulated reward time-course.", encoding="utf-8")
            before = paper.read_text(encoding="utf-8")
            builder = PaperMechanismRegistryBuilder(paper, tmp_path / "artifacts", tmp_path / "out")
            builder.build_report()
            after = paper.read_text(encoding="utf-8")
            self.assertEqual(before, after)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
