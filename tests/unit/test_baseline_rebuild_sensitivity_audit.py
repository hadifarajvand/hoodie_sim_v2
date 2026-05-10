from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.analysis.baseline_rebuild_sensitivity_audit.classifier import (
    SettingSignature,
    build_baseline_signature,
    classify_sensitivity_audit,
)
from src.analysis.baseline_rebuild_sensitivity_audit.gates import validate_feature_gates
from src.analysis.baseline_rebuild_sensitivity_audit.report import BaselineRebuildSensitivityAuditReport, render_markdown
from src.analysis.baseline_rebuild_sensitivity_audit.runner import BaselineRebuildSensitivityAuditRunner
from src.analysis.baseline_rebuild_sensitivity_audit.settings import (
    FIXED_EPISODE_LENGTHS,
    FIXED_SCENARIOS,
    FIXED_SEEDS,
    REUSED_METRICS,
    build_sensitivity_settings,
    supported_baseline_policies,
)


class BaselineRebuildSensitivityAuditUnitTests(unittest.TestCase):
    def test_gate_validation_covers_all_required_artifacts(self) -> None:
        result = validate_feature_gates(
            Path("artifacts/analysis/differential-environment-audit/differential-audit.json"),
            Path("artifacts/analysis/mechanism-repair/repair-summary.json"),
            Path("artifacts/analysis/controlled-mechanistic-sweeps/controlled-mechanistic-sweeps.json"),
            Path("artifacts/analysis/baseline-fairness-rebuild/baseline-fairness-rebuild.json"),
        )

        self.assertTrue(result.passed)
        self.assertEqual([check.artifact for check in result.checks], ["differential_audit", "repair_summary", "controlled_sweeps", "fairness_rebuild"])

    def test_sensitivity_setting_definitions_are_tiny_and_deterministic(self) -> None:
        settings = build_sensitivity_settings()
        self.assertEqual(FIXED_SEEDS, (7, 11, 13))
        self.assertEqual(FIXED_SCENARIOS, ("paper_default", "moderate", "heavy"))
        self.assertEqual(FIXED_EPISODE_LENGTHS, (4, 6))
        self.assertEqual(len(settings), 18)
        self.assertTrue(all(setting.supported for setting in settings))
        self.assertEqual({setting.seed for setting in settings}, {7, 11, 13})
        self.assertEqual({setting.scenario_name for setting in settings}, {"paper_default", "moderate", "heavy"})
        self.assertEqual({setting.episode_length for setting in settings}, {4, 6})

    def test_existing_baselines_are_all_included(self) -> None:
        self.assertEqual(supported_baseline_policies(), ("FLC", "VO", "HO", "RO", "BCO", "MLEO", "ADAPTIVE"))

    def test_shared_environment_and_fairness_controls_are_explicit(self) -> None:
        runner = BaselineRebuildSensitivityAuditRunner(output_dir=Path(tempfile.gettempdir()) / "audit")
        report = runner.run()
        self.assertEqual(report.metadata["feature_id"], "022-baseline-rebuild-sensitivity-audit")
        self.assertEqual(report.sensitivity_dimensions["baseline_signature_fields"], ["completed_tasks", "dropped_tasks", "throughput", "average_delay"])
        self.assertEqual(report.seeds_scenarios_episode_lengths_used["supported_settings"], 18)
        self.assertEqual(report.fairness_controls["shared_environment_interface"], "HoodieGymEnvironment via EvaluationMatrixRunner")
        self.assertTrue(report.fairness_controls["identical_workload"])

    def test_baseline_signature_compaction_is_stable(self) -> None:
        signature = build_baseline_signature({"completed_tasks": 3, "dropped_tasks": 1, "throughput": 2, "average_delay": 4.5})
        self.assertEqual(signature, "completed=3::dropped=1::throughput=2::delay=4.5")

    def test_collapse_stability_classification_supports_all_required_statuses(self) -> None:
        reference = [{"signature": "completed=3::dropped=0::throughput=3::delay=1"}]
        robust = classify_sensitivity_audit(
            reference_signatures=reference,
            setting_signatures=[
                SettingSignature(7, "paper_default", 4, {"FLC": "completed=3::dropped=0::throughput=3::delay=1", "VO": "completed=4::dropped=0::throughput=4::delay=1"}, 2, False, []),
            ],
            supported_settings=build_sensitivity_settings()[:1],
        )
        self.assertEqual(robust.status, "robust_collapse_reduced")

        unchanged = classify_sensitivity_audit(
            reference_signatures=reference,
            setting_signatures=[
                SettingSignature(7, "paper_default", 4, {"FLC": "completed=3::dropped=0::throughput=3::delay=1"}, 1, True, []),
            ],
            supported_settings=build_sensitivity_settings()[:1],
        )
        self.assertEqual(unchanged.status, "collapse_unchanged")

        fragile = classify_sensitivity_audit(
            reference_signatures=[
                {"signature": "completed=3::dropped=0::throughput=3::delay=1"},
                {"signature": "completed=2::dropped=0::throughput=2::delay=1"},
                {"signature": "completed=1::dropped=0::throughput=1::delay=1"},
                {"signature": "completed=4::dropped=0::throughput=4::delay=1"},
            ],
            setting_signatures=[
                SettingSignature(7, "paper_default", 4, {"FLC": "completed=2::dropped=0::throughput=2::delay=2"}, 3, False, []),
                SettingSignature(11, "moderate", 4, {"FLC": "completed=3::dropped=0::throughput=3::delay=1"}, 4, True, []),
            ],
            supported_settings=build_sensitivity_settings()[:2],
        )
        self.assertEqual(fragile.status, "fragile_collapse_reduced")

        worsened = classify_sensitivity_audit(
            reference_signatures=[
                {"signature": "completed=3::dropped=0::throughput=3::delay=1"},
                {"signature": "completed=2::dropped=0::throughput=2::delay=1"},
                {"signature": "completed=1::dropped=0::throughput=1::delay=1"},
                {"signature": "completed=4::dropped=0::throughput=4::delay=1"},
            ],
            setting_signatures=[
                SettingSignature(7, "paper_default", 4, {"FLC": "completed=1::dropped=4::throughput=1::delay=8"}, 1, False, []),
            ],
            supported_settings=build_sensitivity_settings()[:1],
        )
        self.assertEqual(worsened.status, "collapse_worsened")

        inconclusive = classify_sensitivity_audit(
            reference_signatures=reference,
            setting_signatures=[],
            supported_settings=[],
        )
        self.assertEqual(inconclusive.status, "inconclusive")

    def test_fragile_and_inconclusive_results_are_not_bugs(self) -> None:
        report = BaselineRebuildSensitivityAuditReport(
            metadata={
                "feature_id": "022-baseline-rebuild-sensitivity-audit",
                "generated_by": "baseline_rebuild_sensitivity_audit",
                "deterministic": True,
                "source_refs": ["specs/022-baseline-rebuild-sensitivity-audit/spec.md"],
            },
            source_gate_status={"passed": True, "checks": []},
            sensitivity_dimensions={"seeds": [7, 11, 13]},
            seeds_scenarios_episode_lengths_used={"seeds": [7, 11, 13]},
            fairness_controls={"shared_environment_interface": "HoodieGymEnvironment via EvaluationMatrixRunner"},
            included_baselines=["FLC"],
            reused_metrics=list(REUSED_METRICS),
            per_setting_baseline_signatures=[],
            collapse_stability_indicators=[],
            sensitivity_classification={"status": "fragile_collapse_reduced", "notes": ["some settings degraded"]},
            limitations=["Diagnostic only."],
            no_training_disclaimer="No training work was introduced.",
            no_policy_redesign_disclaimer="No policy redesign was introduced.",
            no_metric_change_disclaimer="No metric formula changes were introduced.",
            no_paper_validity_disclaimer="No paper-validity claim is made.",
            reproducibility={"approved_interpreter": "/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python"},
            overall_status="fragile_collapse_reduced",
        )
        markdown = render_markdown(report)
        self.assertIn("No Training Disclaimer", markdown)
        self.assertIn("No Policy Redesign Disclaimer", markdown)
        self.assertIn("No Metric Change Disclaimer", markdown)
        self.assertIn("No Paper Validity Disclaimer", markdown)
        self.assertIn("fragile_collapse_reduced", markdown)


if __name__ == "__main__":
    unittest.main()
