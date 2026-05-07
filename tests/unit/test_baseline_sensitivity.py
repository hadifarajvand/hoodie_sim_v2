from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.analysis.baseline_sensitivity import BaselineSensitivityAnalyzer


class BaselineSensitivityTests(unittest.TestCase):
    def _minimal_root(self, base: Path) -> Path:
        campaign_root = base / "campaign-root"
        (campaign_root / "campaign").mkdir(parents=True, exist_ok=True)
        (campaign_root / "matrix" / "traces").mkdir(parents=True, exist_ok=True)
        (campaign_root / "bundle").mkdir(parents=True, exist_ok=True)
        (campaign_root / "campaign" / "campaign-summary.json").write_text(
            "{\"result_count\": 2, \"mean_average_delay\": 1.0, \"mean_drop_ratio\": 0.0, \"total_completed_tasks\": 4, \"total_dropped_tasks\": 0, \"total_tasks\": 4, \"total_throughput\": 4}",
            encoding="utf-8",
        )
        (campaign_root / "campaign" / "policy-summary.json").write_text(
            "[{\"policy_name\": \"FLC\", \"mean_average_delay\": 1.0, \"total_tasks\": 2}, {\"policy_name\": \"VO\", \"mean_average_delay\": 1.1, \"total_tasks\": 2}]",
            encoding="utf-8",
        )
        (campaign_root / "campaign" / "scenario-summary.json").write_text(
            "[{\"scenario_name\": \"paper_default\", \"mean_average_delay\": 1.0, \"total_tasks\": 2}, {\"scenario_name\": \"moderate\", \"mean_average_delay\": 1.1, \"total_tasks\": 2}]",
            encoding="utf-8",
        )
        (campaign_root / "campaign" / "determinism-check.json").write_text("{\"passed\": true}", encoding="utf-8")
        (campaign_root / "matrix" / "matrix-summary.csv").write_text(
            "policy_name,scenario_name,seed,trace_id,throughput,drop_ratio,average_delay,completed_tasks,dropped_tasks,total_tasks\n"
            "FLC,paper_default,1,paper_default-1,2,0.0,1.0,2,0,2\n"
            "VO,moderate,1,moderate-1,2,0.0,1.1,2,0,2\n",
            encoding="utf-8",
        )
        (campaign_root / "matrix" / "FLC-paper_default-1.json").write_text(
            "{\"policy_name\": \"FLC\", \"scenario_name\": \"paper_default\", \"seed\": 1, \"final_metrics\": {\"average_delay\": 1.0, \"completed_tasks\": 2, \"dropped_tasks\": 0, \"total_tasks\": 2, \"raw_records\": [{\"selected_action\": \"local\", \"terminal_outcome\": \"completed\"}, {\"selected_action\": \"local\", \"terminal_outcome\": \"completed\"}]}}",
            encoding="utf-8",
        )
        (campaign_root / "matrix" / "VO-moderate-1.json").write_text(
            "{\"policy_name\": \"VO\", \"scenario_name\": \"moderate\", \"seed\": 1, \"final_metrics\": {\"average_delay\": 1.1, \"completed_tasks\": 2, \"dropped_tasks\": 0, \"total_tasks\": 2, \"raw_records\": [{\"selected_action\": \"local\", \"terminal_outcome\": \"completed\"}, {\"selected_action\": \"remote\", \"terminal_outcome\": \"completed\"}]}}",
            encoding="utf-8",
        )
        (campaign_root / "matrix" / "traces" / "paper_default-1.json").write_text(
            "{\"trace_id\": \"paper_default-1\", \"seed\": 1, \"metadata\": {\"scenario_name\": \"paper_default\"}, \"tasks\": [{\"arrival_slot\": 0, \"size\": 2.0, \"processing_density\": 0.3}, {\"arrival_slot\": 1, \"size\": 3.0, \"processing_density\": 0.3}]}",
            encoding="utf-8",
        )
        (campaign_root / "matrix" / "traces" / "moderate-1.json").write_text(
            "{\"trace_id\": \"moderate-1\", \"seed\": 1, \"metadata\": {\"scenario_name\": \"moderate\"}, \"tasks\": [{\"arrival_slot\": 0, \"size\": 2.0, \"processing_density\": 0.3}, {\"arrival_slot\": 2, \"size\": 4.0, \"processing_density\": 0.3}]}",
            encoding="utf-8",
        )
        (campaign_root / "bundle" / "manifest.json").write_text("{}", encoding="utf-8")
        (campaign_root / "bundle" / "validation-summary.json").write_text("{}", encoding="utf-8")
        return campaign_root

    def test_identical_and_different_trace_detection(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._minimal_root(Path(tmpdir))
            analyzer = BaselineSensitivityAnalyzer(root, root / "analysis")
            report = analyzer.analyze()

            self.assertTrue(report.trace_comparisons)
            comparison = report.trace_comparisons[0]
            self.assertEqual(comparison["seed"], 1)
            self.assertEqual(comparison["comparison"], "same_count_but_different_slots")
            self.assertTrue(any(item["scenario_name"] == "paper_default" for item in report.scenario_comparisons))
            self.assertTrue(any(item["scenario_name"] == "moderate" for item in report.scenario_comparisons))
            self.assertTrue(report.passed)

    def test_identical_policy_signature_and_near_identical_outcomes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._minimal_root(Path(tmpdir))
            (root / "matrix" / "BCO-paper_default-1.json").write_text(
                "{\"policy_name\": \"BCO\", \"scenario_name\": \"paper_default\", \"seed\": 1, \"final_metrics\": {\"average_delay\": 1.0, \"completed_tasks\": 2, \"dropped_tasks\": 0, \"total_tasks\": 2, \"raw_records\": [{\"selected_action\": \"local\", \"terminal_outcome\": \"completed\"}, {\"selected_action\": \"local\", \"terminal_outcome\": \"completed\"}]}}",
                encoding="utf-8",
            )
            (root / "matrix" / "MLEO-paper_default-1.json").write_text(
                "{\"policy_name\": \"MLEO\", \"scenario_name\": \"paper_default\", \"seed\": 1, \"final_metrics\": {\"average_delay\": 1.0, \"completed_tasks\": 2, \"dropped_tasks\": 0, \"total_tasks\": 2, \"raw_records\": [{\"selected_action\": \"local\", \"terminal_outcome\": \"completed\"}, {\"selected_action\": \"local\", \"terminal_outcome\": \"completed\"}]}}",
                encoding="utf-8",
            )
            analyzer = BaselineSensitivityAnalyzer(root, root / "analysis")
            report = analyzer.analyze()

            self.assertTrue(any(finding["category"] == "policy_behavior_collapsed" for finding in report.findings))
            self.assertEqual(len(report.policy_comparisons), 4)
            signatures = {item["policy_name"]: item["action_signature"] for item in report.policy_comparisons}
            self.assertEqual(signatures["FLC"], signatures["BCO"])
            self.assertEqual(signatures["FLC"], signatures["MLEO"])
            self.assertTrue(any(finding["category"] == "near_identical_outcome_behavior" for finding in report.findings))
            self.assertTrue(all("action_distribution" in item for item in report.policy_comparisons))

    def test_missing_artifacts_are_reported_and_fail_the_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "campaign-root"
            (root / "campaign").mkdir(parents=True, exist_ok=True)
            analyzer = BaselineSensitivityAnalyzer(root, root / "analysis")
            report = analyzer.analyze()

            self.assertFalse(report.passed)
            self.assertTrue(report.missing_artifacts)
            self.assertTrue(any(item["category"] == "missing_artifacts" for item in report.findings))

    def test_deterministic_report_ordering(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._minimal_root(Path(tmpdir))
            analyzer = BaselineSensitivityAnalyzer(root, root / "analysis")
            report_one = analyzer.analyze().to_dict()
            report_two = analyzer.analyze().to_dict()

            self.assertEqual(report_one, report_two)
            self.assertEqual(report_one["findings"], sorted(report_one["findings"], key=lambda item: (item["severity"], item["category"])))


if __name__ == "__main__":
    unittest.main()
