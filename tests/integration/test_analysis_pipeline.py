from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.analysis_runner import AnalysisRunner
from src.analysis.exporter import AnalysisExporter
from src.analysis.plot_builder import PlotBuilder
from src.analysis.report_builder import ReportBuilder
from src.evaluation.comparison_runner import ComparisonRunner
from src.evaluation.config import EvaluationConfig
from src.evaluation.validation_artifacts import build_validation_artifacts
from src.evaluation.validation_runner import ValidationRunner
from src.environment.topology import TopologyGraph
from src.policies.flc import FullLocalComputingPolicy
from src.policies.ho import HorizontalOffloadingPolicy


class AnalysisPipelineTests(unittest.TestCase):
    def _topology(self) -> TopologyGraph:
        return TopologyGraph(
            node_ids=("1", "2", "cloud"),
            legal_adjacency={
                "1": ("2", "cloud"),
                "2": ("1", "cloud"),
            },
        )

    def _config(self) -> EvaluationConfig:
        return EvaluationConfig(policy_name="analysis", seed=37, trace_id="analysis", episode_count=2, episode_length=2)

    def _validation(self):
        topology = self._topology()
        config = self._config()
        return build_validation_artifacts(
            ValidationRunner(
                policies={"FLC": FullLocalComputingPolicy(), "HO": HorizontalOffloadingPolicy()},
                config=config,
                topology=topology,
            ).run()
        )

    def test_metric_integrity_matches_validation_artifacts(self) -> None:
        validation = self._validation()
        analysis = AnalysisRunner(validation).run()

        self.assertEqual(analysis.baseline["trace_results"], validation.validation.policy_results[0].trace_results)
        self.assertEqual(analysis.compared_policies[0].trace_results, validation.validation.policy_results[1].trace_results)

    def test_no_recomputation_in_analysis(self) -> None:
        validation = self._validation()
        analysis = AnalysisRunner(validation).run()
        report = ReportBuilder(analysis).to_dict()

        self.assertEqual(report["baseline"]["trace_results"]["aggregate"], validation.validation.policy_results[0].trace_results["aggregate"])
        self.assertEqual(report["compared_policies"][0]["trace_results"]["aggregate"], validation.validation.policy_results[1].trace_results["aggregate"])

    def test_plot_payload_is_reproducible(self) -> None:
        validation = self._validation()
        analysis = AnalysisRunner(validation).run()
        plot_builder = PlotBuilder(analysis)

        self.assertEqual(plot_builder.to_json(), plot_builder.to_json())
        payload = plot_builder.build_payload()
        self.assertEqual(payload["plots"]["average_delay"], plot_builder.build_payload()["plots"]["average_delay"])
        self.assertTrue(all("policy_name" in row and "trace_id" in row and "seed" in row for row in payload["plots"]["throughput"]))

    def test_report_completeness(self) -> None:
        validation = self._validation()
        analysis = AnalysisRunner(validation).run()
        report = ReportBuilder(analysis)
        payload = report.to_dict()

        self.assertEqual(payload["baseline_policy_name"], "FLC")
        self.assertEqual(payload["policy_order"], ("FLC", "HO"))
        self.assertEqual(payload["baseline"]["policy_name"], "FLC")
        self.assertEqual(payload["compared_policies"][0]["policy_name"], "HO")

    def test_exporter_is_reproducible_for_same_input(self) -> None:
        validation = self._validation()
        analysis = AnalysisRunner(validation).run()
        exporter = AnalysisExporter(ReportBuilder(analysis), PlotBuilder(analysis), timestamp="2026-04-22T00:00:00+00:00")

        with tempfile.TemporaryDirectory() as tmpdir:
            first = exporter.export(Path(tmpdir), deterministic=True)
            second = exporter.export(Path(tmpdir), deterministic=True)
            self.assertEqual(first, second)

            report_data = json.loads(Path(first["report_path"]).read_text(encoding="utf-8"))
            plot_data = json.loads(Path(first["plot_path"]).read_text(encoding="utf-8"))
            self.assertEqual(report_data["report"]["baseline_policy_name"], "FLC")
            self.assertEqual(plot_data["plots"]["baseline_policy_name"], "FLC")
            self.assertEqual(report_data["timestamp"], "2026-04-22T00:00:00+00:00")
            self.assertEqual(plot_data["timestamp"], "2026-04-22T00:00:00+00:00")


if __name__ == "__main__":
    unittest.main()
