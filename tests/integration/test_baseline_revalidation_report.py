from __future__ import annotations

import json
import math
import tempfile
import unittest
from pathlib import Path

from src.analysis.baseline_revalidation_after_runtime_repair import BaselineRevalidationRunner


class BaselineRevalidationReportIntegrationTests(unittest.TestCase):
    def _run_report(self, output_dir: Path, evaluation_output_dir: Path):
        return BaselineRevalidationRunner(
            output_dir=output_dir,
            evaluation_output_dir=evaluation_output_dir,
        ).run()

    def test_baseline_revalidation_result_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            report = self._run_report(tmp / "analysis", tmp / "evaluation")
            payload = report.to_dict()

            required_keys = {
                "feature_id",
                "prerequisite_tags_verified",
                "policies_revalidated",
                "scenarios_revalidated",
                "seeds_used",
                "runtime_contracts_verified",
                "environment_interface_verified",
                "legal_action_mask_verified",
                "metric_schema_verified",
                "deterministic_reproducibility_verified",
                "baseline_result_summary",
                "artifact_paths",
                "no_curve_fitting",
                "no_paper_reproduction_claim",
                "no_dependency_drift",
                "no_training_or_policy_drift",
                "no_environment_contract_drift",
                "no_reward_timing_change",
                "no_execution_time_contract_drift",
                "no_transmission_delay_contract_drift",
                "no_capacity_sharing_contract_drift",
                "no_timeout_contract_drift",
                "final_verdict",
            }
            self.assertTrue(required_keys.issubset(payload))
            self.assertEqual(payload["feature_id"], "037-baseline-revalidation-after-runtime-repair")
            self.assertTrue(payload["no_curve_fitting"])
            self.assertTrue(payload["no_paper_reproduction_claim"])
            self.assertTrue(payload["no_dependency_drift"])
            self.assertTrue(payload["no_training_or_policy_drift"])
            self.assertTrue(payload["no_environment_contract_drift"])
            self.assertTrue(payload["no_reward_timing_change"])
            self.assertTrue(payload["no_execution_time_contract_drift"])
            self.assertTrue(payload["no_transmission_delay_contract_drift"])
            self.assertTrue(payload["no_capacity_sharing_contract_drift"])
            self.assertTrue(payload["no_timeout_contract_drift"])

            summary = payload["baseline_result_summary"]
            self.assertEqual(summary["policy_count"], 7)
            self.assertEqual(summary["scenario_count"], 1)
            self.assertEqual(summary["seed_count"], 3)
            self.assertTrue(summary["legal_action_mask_verified"])
            self.assertTrue(summary["deterministic_reproducibility_verified"])
            self.assertEqual(len(summary["scenario_policy_seed_matrix"]), 21)
            self.assertEqual(summary["topology_source"], "TopologyGraph.from_approved_assumption_registry()")
            self.assertTrue(summary["topology_contract_verified"])
            self.assertEqual(summary["topology_node_count"], 20)
            self.assertEqual(summary["topology_degree_sequence"], [3] * 20)
            self.assertEqual(summary["topology_undirected_edge_count"], 30)
            self.assertTrue(summary["topology_zero_diagonal_verified"])
            self.assertTrue(summary["topology_symmetric_verified"])
            self.assertTrue(summary["neighbor_only_horizontal_legality_verified"])
            self.assertTrue(summary["vertical_cloud_legality_independent_of_figure7_verified"])
            self.assertGreater(summary["generated_arrivals"], 0)
            self.assertGreaterEqual(summary["generated_arrivals"], summary["finalized_terminal_tasks"])
            self.assertGreaterEqual(summary["generated_arrivals"], summary["pending_at_horizon"])
            self.assertGreaterEqual(summary["total_terminal_tasks"], summary["finalized_terminal_tasks"])

    def test_baseline_revalidation_artifacts_are_written(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            report = self._run_report(tmp / "analysis", tmp / "evaluation")
            analysis_dir = tmp / "analysis"
            evaluation_dir = tmp / "evaluation"

            json_path = analysis_dir / "baseline-revalidation-report.json"
            md_path = analysis_dir / "baseline-revalidation-report.md"
            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())
            self.assertTrue(any(evaluation_dir.glob("*.json")))
            self.assertTrue((evaluation_dir / "revalidation-summary.csv").exists())
            self.assertIn(str(json_path), report.artifact_paths)
            self.assertIn(str(md_path), report.artifact_paths)
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["feature_id"], "037-baseline-revalidation-after-runtime-repair")

    def test_no_curve_fitting_or_paper_reproduction_claim(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report = self._run_report(Path(tmpdir) / "analysis", Path(tmpdir) / "evaluation")
            payload = report.to_dict()

            self.assertTrue(payload["no_curve_fitting"])
            self.assertTrue(payload["no_paper_reproduction_claim"])
            self.assertIn("without_curve_fitting", payload["final_verdict"])
            self.assertNotIn("reproduction", payload["final_verdict"].lower())

    def test_metric_schema_and_numeric_sanity(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report = self._run_report(Path(tmpdir) / "analysis", Path(tmpdir) / "evaluation")
            metrics = report.baseline_result_summary["metrics"]

            self.assertTrue(metrics)
            for metric in metrics:
                self.assertEqual(metric["total_tasks"], metric["completed_tasks"] + metric["dropped_tasks"])
                self.assertGreaterEqual(float(metric["drop_ratio"]), 0.0)
                self.assertLessEqual(float(metric["drop_ratio"]), 1.0)
                if metric["completed_tasks"] > 0:
                    self.assertGreaterEqual(float(metric["average_delay"]), 0.0)
                for key in ("average_delay", "drop_ratio", "throughput"):
                    self.assertTrue(math.isfinite(float(metric[key])))

    def test_revalidation_trace_artifacts_are_non_empty_valid_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            self._run_report(tmp / "analysis", tmp / "evaluation")

            trace_dir = tmp / "evaluation" / "traces"
            trace_files = sorted(trace_dir.glob("*.json"))
            self.assertEqual(len(trace_files), 3)
            for path in trace_files:
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertIn("trace_id", payload)
                self.assertIn("tasks", payload)
                self.assertTrue(payload["tasks"])

    def test_revalidation_reports_generated_finalized_and_pending_task_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report = self._run_report(Path(tmpdir) / "analysis", Path(tmpdir) / "evaluation")
            summary = report.baseline_result_summary

            self.assertIn("generated_arrivals", summary)
            self.assertIn("finalized_terminal_tasks", summary)
            self.assertIn("completed_tasks", summary)
            self.assertIn("dropped_tasks", summary)
            self.assertIn("pending_at_horizon", summary)
            self.assertIn("total_terminal_tasks", summary)
            self.assertGreater(summary["generated_arrivals"], 0)
            self.assertGreaterEqual(summary["generated_arrivals"], summary["finalized_terminal_tasks"])
            self.assertGreaterEqual(summary["generated_arrivals"], summary["pending_at_horizon"])
            self.assertEqual(summary["finalized_terminal_tasks"], summary["completed_tasks"] + summary["dropped_tasks"])


if __name__ == "__main__":
    unittest.main()
