from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src.analysis.completion_root_cause_diagnosis import run_completion_root_cause_diagnosis
from src.analysis.completion_root_cause_diagnosis.runner import build_completion_root_cause_report


class CompletionRootCauseReportIntegrationTests(unittest.TestCase):
    def test_report_writes_json_and_markdown_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "artifacts/analysis/completion-root-cause-diagnosis"
            report = run_completion_root_cause_diagnosis(output_dir=output_dir)
            json_path = output_dir / "completion-root-cause-report.json"
            md_path = output_dir / "completion-root-cause-report.md"
            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["feature_id"], report.feature_id)
            self.assertTrue(payload["no_paper_reproduction_claim"])

    def test_report_uses_paper_default_trace_sample_constraints(self) -> None:
        report = run_completion_root_cause_diagnosis()
        sample = report.lifecycle_trace_sample
        self.assertTrue(sample)
        first = sample[0]
        self.assertGreaterEqual(first["size_mbits"], 2.0)
        self.assertLessEqual(first["size_mbits"], 5.0)
        self.assertEqual(first["processing_density_gcycles_per_mbit"], 0.297)
        self.assertEqual(first["absolute_deadline_slot"] - first["arrival_slot"], 20)
        self.assertEqual(report.paper_default_runtime_verified["episode_length"], 110)
        self.assertEqual(report.paper_default_runtime_verified["timeout_slots"], 20)

    def test_report_marks_pointer_only_dirty_workspace_as_clean_enough(self) -> None:
        from src.analysis.completion_root_cause_diagnosis import report as report_module

        with mock.patch.object(report_module, "_tracked_dirty_paths", return_value=[".specify/feature.json"]):
            tags = report_module.build_prerequisite_tags_verified()
            dirty_tag = next(entry for entry in tags if entry["name"] == "no_unrelated_dirty_files")
            self.assertTrue(dirty_tag["verified"])
            self.assertNotIn("AGENTS.md", dirty_tag["details"])

    def test_report_generation_blocks_agents_dirty_workspace(self) -> None:
        from src.analysis.completion_root_cause_diagnosis import report as report_module

        with mock.patch.object(report_module, "_tracked_dirty_paths", return_value=["AGENTS.md"]):
            with self.assertRaises(RuntimeError):
                build_completion_root_cause_report()

    def test_report_recommends_next_feature_without_repair(self) -> None:
        report = run_completion_root_cause_diagnosis()
        payload = report.to_dict()
        self.assertTrue(payload["no_runtime_repair_performed"])
        self.assertIsNotNone(payload["recommended_next_feature"])
        self.assertIn(payload["recommended_next_feature"], {
            "Feature 046 - Runtime Repair for Completion Lifecycle",
            "observation vector follow-up",
            "exploration schedule follow-up",
            "loss-sequence follow-up",
            "load/configuration audit follow-up",
        })

    def test_no_unrelated_dirty_files_is_true_and_agents_not_mentioned(self) -> None:
        report = run_completion_root_cause_diagnosis()
        dirty_tag = next(entry for entry in report.prerequisite_tags_verified if entry["name"] == "no_unrelated_dirty_files")
        self.assertTrue(dirty_tag["verified"])
        self.assertNotIn("AGENTS.md", dirty_tag["details"])
        self.assertTrue(all(entry["verified"] for entry in report.prior_feature_gates_verified))


if __name__ == "__main__":
    unittest.main()
