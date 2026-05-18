from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.paper_default_terminal_exposure_probe import (
    TerminalExposureProbeConfig,
    generate_terminal_exposure_artifacts,
    run_terminal_exposure_probe,
    write_terminal_exposure_report,
)


class PaperDefaultTerminalExposureReportIntegrationTests(unittest.TestCase):
    def test_campaign_report_schema(self) -> None:
        report = run_terminal_exposure_probe(TerminalExposureProbeConfig())
        payload = report.to_dict()
        self.assertEqual(payload["feature_id"], "042-paper-default-terminal-exposure-probe")
        self.assertIn(payload["final_verdict"], {"terminal_exposure_present", "terminal_exposure_absent_under_paper_default"})
        self.assertTrue(payload["no_training_started"])
        self.assertTrue(payload["no_optimizer_step"])
        self.assertTrue(payload["no_replay_training"])
        self.assertTrue(payload["no_target_update_execution"])
        self.assertTrue(payload["no_dependency_drift"])
        self.assertTrue(payload["no_environment_contract_drift"])
        self.assertTrue(payload["no_policy_drift"])
        self.assertTrue(payload["no_reward_timing_change"])
        self.assertTrue(payload["no_curve_fitting"])
        self.assertTrue(payload["no_simulator_output_tuning"])
        self.assertTrue(payload["no_paper_reproduction_claim"])
        self.assertIn("diagnosis", payload)
        self.assertIn("recommended_next_feature", payload)
        self.assertIn("prerequisite_tags_verified", payload)
        self.assertIn("prior_feature_gates_verified", payload)

    def test_report_claims_no_reproduction_or_training_and_writes_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report, json_path, markdown_path = generate_terminal_exposure_artifacts(
                TerminalExposureProbeConfig(),
                output_dir=Path(tmpdir) / "artifacts/analysis/paper-default-terminal-exposure-probe",
            )
            self.assertTrue(json_path.exists())
            self.assertTrue(markdown_path.exists())
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["feature_id"], "042-paper-default-terminal-exposure-probe")
            self.assertTrue(payload["no_paper_reproduction_claim"])
            self.assertTrue(payload["no_training_started"])
            self.assertTrue(payload["no_optimizer_step"])
            self.assertTrue(payload["no_replay_training"])
            self.assertIsNotNone(report.final_verdict)

    def test_report_requires_required_audit_flags(self) -> None:
        report = run_terminal_exposure_probe(TerminalExposureProbeConfig())
        self.assertTrue(report.no_training_started)
        self.assertTrue(report.no_optimizer_step)
        self.assertTrue(report.no_replay_training)
        self.assertTrue(report.no_target_update_execution)

    def test_report_rejects_paper_reproduction_claim(self) -> None:
        report = run_terminal_exposure_probe(TerminalExposureProbeConfig())
        self.assertTrue(report.no_paper_reproduction_claim)

    def test_report_rejects_training_approval(self) -> None:
        report = run_terminal_exposure_probe(TerminalExposureProbeConfig())
        self.assertEqual(report.final_verdict, "terminal_exposure_absent_under_paper_default" if report.aggregate_terminal_exposure_summary["reward_bearing_transition_count"] == 0 else "terminal_exposure_present")

    def test_prerequisite_pointer_not_staged_true_when_local_only_pointer(self) -> None:
        from src.analysis.paper_default_terminal_exposure_probe.report import build_prerequisite_tags_verified

        tags = build_prerequisite_tags_verified()
        pointer_not_staged = next(item for item in tags if item["name"] == "pointer_not_staged")
        pointer_not_in_main_head = next(item for item in tags if item["name"] == "pointer_not_in_main_head")
        self.assertTrue(pointer_not_staged["verified"])
        self.assertTrue(pointer_not_in_main_head["verified"])

    def test_feature_038_prerequisite_uses_training_foundation_contract_report_path(self) -> None:
        from src.analysis.paper_default_terminal_exposure_probe.report import collect_prior_feature_gates_verified

        tags = collect_prior_feature_gates_verified()
        feature_038 = next(item for item in tags if item["feature"] == "038")
        self.assertIn(
            "training-foundation-contract-report.json",
            feature_038["details"],
        )
        self.assertTrue(feature_038["verified"])


if __name__ == "__main__":
    unittest.main()
