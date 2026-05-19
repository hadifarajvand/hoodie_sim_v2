from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.task_completion_lifecycle_formula_audit import CompletionLifecycleAuditConfig, run_completion_lifecycle_audit


class TaskCompletionLifecycleReportIntegrationTests(unittest.TestCase):
    def test_report_writes_json_and_markdown_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "artifacts/analysis/task-completion-lifecycle-formula-audit"
            report = run_completion_lifecycle_audit(CompletionLifecycleAuditConfig(), output_dir=output_dir)
            json_path = output_dir / "completion-lifecycle-audit-report.json"
            md_path = output_dir / "completion-lifecycle-audit-report.md"
            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["feature_id"], report.feature_id)
            self.assertTrue(payload["no_paper_reproduction_claim"])

    def test_report_contains_required_diagnosis_fields(self) -> None:
        report = run_completion_lifecycle_audit(CompletionLifecycleAuditConfig())
        payload = report.to_dict()
        self.assertIn("completion_absence_diagnosis", payload)
        self.assertIn("suspected_root_causes", payload)
        self.assertIn("recommended_next_feature", payload)
        self.assertTrue(all(entry["verified"] for entry in payload["prior_feature_gates_verified"]))
        self.assertIn(payload["final_verdict"], {
            "completion_lifecycle_valid",
            "completion_lifecycle_counter_bug_detected",
            "completion_lifecycle_runtime_bug_detected",
            "completion_absence_explained_by_queue_pressure",
            "formula_mismatch_detected",
            "audit_inconclusive_requires_runtime_trace_instrumentation",
            "prerequisite_blocked",
        })
        self.assertEqual(payload["completion_absence_diagnosis"], "insufficient_lifecycle_trace_metadata")
        self.assertEqual(payload["recommended_next_feature"], "passive_runtime_lifecycle_trace_instrumentation")
        dirty_tag = next(entry for entry in payload["prerequisite_tags_verified"] if entry["name"] == "no_unrelated_dirty_files")
        self.assertFalse(dirty_tag["verified"])
        self.assertIn("AGENTS.md", dirty_tag["details"])
        main_gate = next(entry for entry in payload["prerequisite_tags_verified"] if entry["name"] == "main_equals_feature_042")
        self.assertIn("042-paper-default-terminal-exposure-probe-complete^{}", main_gate["details"])


if __name__ == "__main__":
    unittest.main()
