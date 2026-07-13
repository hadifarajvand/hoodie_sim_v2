from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src.analysis.completion_root_cause_diagnosis import CompletionRootCauseReport, run_completion_root_cause_diagnosis
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

    def test_report_allows_explicit_test_override_for_dirty_workspace(self) -> None:
        from src.analysis.completion_root_cause_diagnosis import report as report_module

        with mock.patch.dict(report_module.os.environ, {"ECHO_TEST_ALLOW_DIRTY_WORKTREE": "1"}, clear=False):
            with mock.patch.object(report_module, "_tracked_dirty_paths", return_value=["src/environment/environment.py"]):
                tags = report_module.build_prerequisite_tags_verified()
                dirty_tag = next(entry for entry in tags if entry["name"] == "no_unrelated_dirty_files")
                self.assertFalse(dirty_tag["verified"])
                self.assertIn("src/environment/environment.py", dirty_tag["details"])
                report = build_completion_root_cause_report()
                self.assertFalse(report.prerequisite_tags_verified[-1]["verified"])

    def test_report_recommends_next_feature_without_repair(self) -> None:
        report = run_completion_root_cause_diagnosis()
        payload = report.to_dict()
        self.assertTrue(payload["no_runtime_repair_performed"])
        self.assertIsNotNone(payload["recommended_next_feature"])
        self.assertIn(payload["recommended_next_feature"], {
            "Feature 046 - Runtime Repair for Completion Lifecycle",
            "observation/exploration/loss sequence",
            "load/admission/action-exposure review",
        })
        self.assertEqual(payload["final_verdict"], "root_cause_identified_configuration_or_load_explanation")

    def test_no_unrelated_dirty_files_is_true_and_agents_not_mentioned(self) -> None:
        from src.analysis.completion_root_cause_diagnosis import report as report_module

        with mock.patch.dict(report_module.os.environ, {}, clear=False):
            with mock.patch.object(report_module, "_tracked_dirty_paths", return_value=[".specify/feature.json"]):
                report = run_completion_root_cause_diagnosis()
                dirty_tag = next(entry for entry in report.prerequisite_tags_verified if entry["name"] == "no_unrelated_dirty_files")
                self.assertTrue(dirty_tag["verified"])
                self.assertNotIn("AGENTS.md", dirty_tag["details"])
                self.assertTrue(all(entry["verified"] for entry in report.prior_feature_gates_verified))

    def test_runtime_repair_verdict_requires_runtime_fault_evidence(self) -> None:
        payload = copy.deepcopy(run_completion_root_cause_diagnosis().to_dict())
        payload["final_verdict"] = "root_cause_identified_runtime_repair_required"
        payload["recommended_next_feature"] = "Feature 046 - Runtime Repair for Completion Lifecycle"
        for entry in payload["root_cause_evaluations"]:
            if entry["root_cause_class"] in {
                "completion_emitted_but_reward_or_counter_path_wrong",
                "deadline_drop_ordering_issue",
                "formula_unit_mismatch",
            }:
                entry["detected"] = False
                entry["evidence_count"] = 0
                entry["confidence"] = "low"
        with self.assertRaises(ValueError):
            CompletionRootCauseReport(**payload)

    def test_runtime_repair_verdict_rejects_low_or_empty_runtime_fault_evidence(self) -> None:
        for confidence, evidence_count in [("low", 2), ("medium", 0)]:
            payload = copy.deepcopy(run_completion_root_cause_diagnosis().to_dict())
            payload["final_verdict"] = "root_cause_identified_runtime_repair_required"
            payload["recommended_next_feature"] = "Feature 046 - Runtime Repair for Completion Lifecycle"
            entry = {
                "root_cause_class": "formula_unit_mismatch",
                "evaluated": True,
                "detected": True,
                "evidence_count": evidence_count,
                "supporting_event_types": ["task_generated", "execution_progress"],
                "representative_task_ids": ["synthetic:1"],
                "explanation": "synthetic",
                "confidence": confidence,
                "required_next_action": "synthetic",
            }
            payload["root_cause_evaluations"] = [entry]
            with self.subTest(confidence=confidence, evidence_count=evidence_count):
                with self.assertRaises(ValueError):
                    CompletionRootCauseReport(**payload)

    def test_recommended_next_feature_must_match_final_verdict(self) -> None:
        payload = copy.deepcopy(run_completion_root_cause_diagnosis().to_dict())
        payload["final_verdict"] = "root_cause_identified_configuration_or_load_explanation"
        payload["recommended_next_feature"] = "Feature 046 - Runtime Repair for Completion Lifecycle"
        with self.assertRaises(ValueError):
            CompletionRootCauseReport(**payload)

        payload = copy.deepcopy(run_completion_root_cause_diagnosis().to_dict())
        payload["final_verdict"] = "root_cause_identified_policy_or_action_exposure_issue"
        payload["recommended_next_feature"] = "load/admission/action-exposure review"
        with self.assertRaises(ValueError):
            CompletionRootCauseReport(**payload)

        payload = copy.deepcopy(run_completion_root_cause_diagnosis().to_dict())
        payload["final_verdict"] = "root_cause_identified_configuration_or_load_explanation"
        payload["recommended_next_feature"] = "observation/exploration/loss sequence"
        with self.assertRaises(ValueError):
            CompletionRootCauseReport(**payload)

    def test_execution_progress_deadline_expires_first_alone_does_not_trigger_runtime_repair(self) -> None:
        payload = copy.deepcopy(run_completion_root_cause_diagnosis().to_dict())
        payload["final_verdict"] = "root_cause_identified_runtime_repair_required"
        payload["recommended_next_feature"] = "Feature 046 - Runtime Repair for Completion Lifecycle"
        payload["root_cause_evaluations"] = [
            {
                "root_cause_class": "execution_progress_deadline_expires_first",
                "evaluated": True,
                "detected": True,
                "evidence_count": 3,
                "supporting_event_types": ["execution_progress", "deadline_expired", "task_dropped"],
                "representative_task_ids": ["synthetic:1"],
                "explanation": "synthetic",
                "confidence": "high",
                "required_next_action": "synthetic",
            }
        ]
        with self.assertRaises(ValueError):
            CompletionRootCauseReport(**payload)

    def test_no_completion_problem_detected_does_not_recommend_runtime_repair(self) -> None:
        payload = copy.deepcopy(run_completion_root_cause_diagnosis().to_dict())
        payload["final_verdict"] = "no_completion_problem_detected"
        payload["recommended_next_feature"] = "Feature 046 - Runtime Repair for Completion Lifecycle"
        with self.assertRaises(ValueError):
            CompletionRootCauseReport(**payload)


if __name__ == "__main__":
    unittest.main()
