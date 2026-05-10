from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from src.analysis.hoodie_training_foundation_readiness_audit.gates import REQUIRED_SOURCE_ARTIFACTS, validate_feature_gates
from src.analysis.hoodie_training_foundation_readiness_audit.readiness import classify_readiness
from src.analysis.hoodie_training_foundation_readiness_audit.report import ReadinessAuditReport, build_readiness_report, render_markdown
from src.analysis.hoodie_training_foundation_readiness_audit.runner import HoodieTrainingFoundationReadinessAuditRunner


class HoodieTrainingFoundationReadinessAuditUnitTests(unittest.TestCase):
    def _source_gate_status(self) -> dict[str, object]:
        return validate_feature_gates(*[path for _name, path in REQUIRED_SOURCE_ARTIFACTS]).to_dict()

    def test_feature_gates_validate_committed_artifacts(self) -> None:
        result = validate_feature_gates(*[path for _name, path in REQUIRED_SOURCE_ARTIFACTS])
        self.assertTrue(result.passed)
        self.assertEqual([check.artifact for check in result.checks], [name for name, _ in REQUIRED_SOURCE_ARTIFACTS])
        self.assertEqual(result.checks[0].path, str(REQUIRED_SOURCE_ARTIFACTS[0][1]))

    def test_missing_required_artifact_is_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            missing = [path for _name, path in REQUIRED_SOURCE_ARTIFACTS]
            missing[0] = tmp_path / "missing.tex"
            result = validate_feature_gates(*missing)
            self.assertFalse(result.passed)
            self.assertFalse(result.checks[0].valid)

    def test_readiness_dimensions_and_verdict_are_blocked_when_training_foundations_are_missing(self) -> None:
        gate_status = self._source_gate_status()
        report = classify_readiness(gate_status, {"paper_ocr_text": Path(REQUIRED_SOURCE_ARTIFACTS[0][1]).read_text(encoding="utf-8")})
        self.assertEqual(report.verdict, "blocked_readiness")
        names = [dimension.name for dimension in report.dimensions]
        self.assertEqual(
            names,
            [
                "state_representation",
                "action_space_legality",
                "delayed_reward_timing",
                "episode_protocol",
                "replay_log_artifacts",
                "dqn_mechanism_gap",
                "double_dqn_mechanism_gap",
                "dueling_dqn_mechanism_gap",
                "lstm_mechanism_gap",
                "training_evaluation_separation",
                "reproducibility",
                "pre_training_blockers",
            ],
        )
        self.assertTrue(any("training/evaluation split" in blocker for blocker in report.blockers))

    def test_mechanism_gap_classification_and_report_schema_are_present(self) -> None:
        gate_status = self._source_gate_status()
        audit = classify_readiness(gate_status, {"paper_ocr_text": Path(REQUIRED_SOURCE_ARTIFACTS[0][1]).read_text(encoding="utf-8")})
        report = build_readiness_report(audit, gate_status, [str(path) for _name, path in REQUIRED_SOURCE_ARTIFACTS])
        payload = report.to_dict()
        self.assertEqual(
            set(payload),
            {
                "metadata",
                "source_gate_status",
                "readiness_dimensions",
                "included_source_artifacts",
                "mechanism_gaps",
                "blockers",
                "verdict",
                "limitations",
                "disclaimers",
                "reproducibility_details",
            },
        )
        self.assertEqual([gap["family"] for gap in payload["mechanism_gaps"]], ["DQN", "Double-DQN", "Dueling-DQN", "LSTM"])
        markdown = render_markdown(report)
        self.assertIn("No DRL training", markdown)
        self.assertIn("training/evaluation split", markdown)

    def test_input_loading_is_deterministic_and_does_not_mutate_source_files(self) -> None:
        source_file = Path(REQUIRED_SOURCE_ARTIFACTS[0][1])
        before = source_file.read_text(encoding="utf-8")
        gate_status = self._source_gate_status()
        report1 = classify_readiness(gate_status, {"paper_ocr_text": before})
        report2 = classify_readiness(gate_status, {"paper_ocr_text": before})
        self.assertEqual(report1.to_dict(), report2.to_dict())
        self.assertEqual(before, source_file.read_text(encoding="utf-8"))

    def test_runner_writes_json_and_markdown_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "audit"
            report1 = HoodieTrainingFoundationReadinessAuditRunner(output_dir=output_dir).run()
            first_snapshot = {path.name: path.read_text(encoding="utf-8") for path in sorted(output_dir.iterdir()) if path.is_file()}
            report2 = HoodieTrainingFoundationReadinessAuditRunner(output_dir=output_dir).run()
            second_snapshot = {path.name: path.read_text(encoding="utf-8") for path in sorted(output_dir.iterdir()) if path.is_file()}

            self.assertEqual(report1.to_dict(), report2.to_dict())
            self.assertEqual(first_snapshot, second_snapshot)
            self.assertTrue((output_dir / "hoodie-training-foundation-readiness-audit.json").exists())
            self.assertTrue((output_dir / "hoodie-training-foundation-readiness-audit.md").exists())
            self.assertTrue((output_dir / "hoodie-training-foundation-readiness-audit.csv").exists())
            self.assertEqual(report1.verdict, "blocked_readiness")
            self.assertEqual(report1.metadata["feature_id"], "023-training-foundation-readiness-audit")


if __name__ == "__main__":
    unittest.main()
