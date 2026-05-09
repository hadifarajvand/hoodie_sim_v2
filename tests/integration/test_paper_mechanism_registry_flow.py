from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import tempfile
import unittest

from src.analysis.paper_mechanism_registry import PaperMechanismRegistryBuilder


def _hash_tree(root: Path) -> dict[str, str]:
    snapshot: dict[str, str] = {}
    if not root.exists():
        return snapshot
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        digest = sha256(path.read_bytes()).hexdigest()
        snapshot[path.relative_to(root).as_posix()] = digest
    return snapshot


class PaperMechanismRegistryFlowTests(unittest.TestCase):
    def test_registry_generation_against_real_sources_is_deterministic(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        paper = repo_root / "resources/papers/hoodie/ocr/merged.tex"
        artifact_root = repo_root / "artifacts"
        campaign_root = repo_root / "artifacts/campaigns/paper-baseline-reproduction"
        before_hashes = _hash_tree(campaign_root)

        with tempfile.TemporaryDirectory() as tmp:
            out1 = Path(tmp) / "out1"
            out2 = Path(tmp) / "out2"
            builder1 = PaperMechanismRegistryBuilder(paper, artifact_root, out1)
            report1 = builder1.run()
            builder2 = PaperMechanismRegistryBuilder(paper, artifact_root, out2)
            report2 = builder2.run()

            json1 = out1 / "paper-mechanism-registry.json"
            md1 = out1 / "paper-mechanism-registry.md"
            json2 = out2 / "paper-mechanism-registry.json"
            md2 = out2 / "paper-mechanism-registry.md"

            self.assertTrue(json1.exists())
            self.assertTrue(md1.exists())
            self.assertTrue(json2.exists())
            self.assertTrue(md2.exists())
            self.assertEqual(json1.read_bytes(), json2.read_bytes())
            self.assertEqual(md1.read_bytes(), md2.read_bytes())
            self.assertTrue(report1.read_only)
            self.assertFalse(report1.behavior_changes)
            self.assertEqual(len(report1.mechanism_entries), 25)
            self.assertEqual(len(report2.mechanism_entries), 25)
            self.assertEqual([entry.category for entry in report1.mechanism_entries], [entry.category for entry in report2.mechanism_entries])
            self.assertNotEqual(report1.implementation_gap_summary["implemented"], 23)
            self.assertEqual(report1.implementation_gap_summary["paper_validated"], 0)
            self.assertGreater(report1.implementation_gap_summary["mapped_but_unvalidated"], 0)
            self.assertGreater(report1.implementation_gap_summary["partially_implemented"], 0)

            payload = json1.read_text(encoding="utf-8")
            self.assertIn('"registry_version": "016"', payload)
            self.assertIn('"read_only": true', payload)
            self.assertIn('"behavior_changes": false', payload)
            self.assertIn('"mapped_in_project"', payload)
            self.assertIn('"mapped_but_unvalidated"', payload)
            self.assertIn('"paper_validated"', payload)
            self.assertIn('"system_topology"', payload)
            self.assertIn('"reward_definition"', payload)
            self.assertIn('"timeout_and_drop"', payload)

        after_hashes = _hash_tree(campaign_root)
        self.assertEqual(before_hashes, after_hashes)

    def test_topology_and_high_risk_entries_are_classified(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        paper = repo_root / "resources/papers/hoodie/ocr/merged.tex"
        artifact_root = repo_root / "artifacts"
        with tempfile.TemporaryDirectory() as tmp:
            builder = PaperMechanismRegistryBuilder(paper, artifact_root, Path(tmp) / "out")
            report = builder.build_report()
            topology = next(entry for entry in report.mechanism_entries if entry.category == "system_topology")
            reward = next(entry for entry in report.mechanism_entries if entry.category == "reward_definition")
            timeout = next(entry for entry in report.mechanism_entries if entry.category == "timeout_and_drop")
            training = next(entry for entry in report.mechanism_entries if entry.category == "dqn_double_dueling_lstm_training")
            self.assertEqual(topology.assumption_risk, "blocking")
            self.assertIn(topology.next_action, {"requires_reference_kernel", "inspect_source"})
            self.assertEqual(reward.assumption_risk, "blocking")
            self.assertEqual(timeout.assumption_risk, "blocking")
            self.assertIn(training.implementation_status, {"unknown", "partially_implemented"})
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


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
