from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.analysis.baseline_fairness_rebuild.classify import classify_collapse
from src.analysis.baseline_fairness_rebuild.gates import validate_feature_gates
from src.analysis.baseline_fairness_rebuild.report import BaselineFairnessRebuildReport, render_markdown


class BaselineFairnessRebuildUnitTests(unittest.TestCase):
    def test_feature_gates_validate_committed_artifacts(self) -> None:
        result = validate_feature_gates(
            Path("artifacts/analysis/differential-environment-audit/differential-audit.json"),
            Path("artifacts/analysis/mechanism-repair/repair-summary.json"),
            Path("artifacts/analysis/controlled-mechanistic-sweeps/controlled-mechanistic-sweeps.json"),
        )

        self.assertTrue(result.passed)
        self.assertEqual([check.artifact for check in result.checks], ["differential_audit", "repair_summary", "controlled_sweeps"])

    def test_collapse_classification_supports_all_required_statuses(self) -> None:
        unchanged = classify_collapse(
            [
                {"policy_name": "FLC", "scenario_name": "paper_default", "final_metrics": {"completed_tasks": 2, "dropped_tasks": 0, "throughput": 2}},
                {"policy_name": "VO", "scenario_name": "paper_default", "final_metrics": {"completed_tasks": 2, "dropped_tasks": 0, "throughput": 2}},
            ]
        )
        self.assertEqual(unchanged.status, "collapse_unchanged")

        reduced = classify_collapse(
            [
                {"policy_name": "FLC", "scenario_name": "paper_default", "final_metrics": {"completed_tasks": 1, "dropped_tasks": 0, "throughput": 1}},
                {"policy_name": "VO", "scenario_name": "paper_default", "final_metrics": {"completed_tasks": 1, "dropped_tasks": 1, "throughput": 1}},
            ]
        )
        self.assertEqual(reduced.status, "collapse_reduced")

        worsened = classify_collapse(
            [
                {"policy_name": "FLC", "scenario_name": "paper_default", "final_metrics": {"completed_tasks": 0, "dropped_tasks": 4, "throughput": 0}},
                {"policy_name": "VO", "scenario_name": "paper_default", "final_metrics": {"completed_tasks": 0, "dropped_tasks": 4, "throughput": 0}},
            ]
        )
        self.assertEqual(worsened.status, "collapse_worsened")

        inconclusive = classify_collapse([])
        self.assertEqual(inconclusive.status, "inconclusive")

    def test_report_schema_and_disclaimers_are_present(self) -> None:
        report = BaselineFairnessRebuildReport(
            metadata={
                "feature_id": "021-baseline-fairness-rebuild",
                "generated_by": "baseline_fairness_rebuild",
                "deterministic": True,
                "source_refs": ["specs/021-baseline-fairness-rebuild/spec.md"],
            },
            source_gate_status={"passed": True, "checks": []},
            baseline_policies_included=["FLC", "VO"],
            scenarios_traces_used=[{"scenario_name": "paper_default", "seed": 7, "trace_id": "paper_default-7"}],
            fairness_controls={"shared_environment_interface": "HoodieGymEnvironment"},
            metrics_reused=["completed_tasks", "dropped_tasks"],
            collapse_indicators=[{"policy_name": "FLC", "scenario_name": "paper_default", "signature": "completed=1|dropped=0|throughput=1"}],
            anti_collapse_assessment={"status": "collapse_unchanged", "policy_diversity": 1, "evidence": ["baseline signatures remained identical"]},
            unchanged_collapse_explanation="Persistent collapse remains a valid mechanism property.",
            limitations=["Diagnostic only."],
            no_training_disclaimer="No training work was introduced.",
            no_policy_redesign_disclaimer="No policy redesign was introduced.",
            no_paper_validity_disclaimer="No paper-validity claim is made.",
            reproducibility_details={"approved_interpreter": "/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python"},
            overall_status="collapse_unchanged",
        )

        payload = report.to_dict()
        self.assertEqual(
            set(payload),
            {
                "metadata",
                "source_gate_status",
                "baseline_policies_included",
                "scenarios_traces_used",
                "fairness_controls",
                "metrics_reused",
                "collapse_indicators",
                "anti_collapse_assessment",
                "unchanged_collapse_explanation",
                "limitations",
                "no_training_disclaimer",
                "no_policy_redesign_disclaimer",
                "no_paper_validity_disclaimer",
                "reproducibility_details",
                "overall_status",
            },
        )
        markdown = render_markdown(report)
        self.assertIn("No Training Disclaimer", markdown)
        self.assertIn("No Policy Redesign Disclaimer", markdown)
        self.assertIn("No Paper Validity Disclaimer", markdown)
        self.assertIn("Persistent collapse remains a valid mechanism property.", markdown)


if __name__ == "__main__":
    unittest.main()
