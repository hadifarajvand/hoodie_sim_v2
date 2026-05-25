from __future__ import annotations

import json
from pathlib import Path
import unittest

from src.analysis.evaluation_trace_bank_baseline_harness import generate_evaluation_trace_bank_baseline_harness_artifacts


class EvaluationTraceBankBaselineHarnessReportIntegrationTests(unittest.TestCase):
    def test_report_artifacts_are_generated(self) -> None:
        report, json_path, md_path = generate_evaluation_trace_bank_baseline_harness_artifacts()
        self.assertTrue(json_path.exists())
        self.assertTrue(md_path.exists())
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["feature_id"], report.feature_id)
        self.assertEqual(payload["final_verdict"], "evaluation_trace_bank_baseline_harness_ready")
        self.assertEqual(payload["remaining_blockers"], [])

    def test_markdown_report_mentions_required_sections(self) -> None:
        generate_evaluation_trace_bank_baseline_harness_artifacts()
        markdown = Path("artifacts/analysis/evaluation-trace-bank-baseline-harness/evaluation-trace-bank-baseline-harness-report.md").read_text(encoding="utf-8")
        self.assertIn("Evaluation Trace Bank Baseline Harness Report", markdown)
        self.assertIn("## Evaluation Trace Bank Summary", markdown)
        self.assertIn("## Baseline Evaluation Harness Summary", markdown)
        self.assertIn("## Determinism Summary", markdown)

    def test_report_does_not_claim_performance_or_reproduction(self) -> None:
        payload = generate_evaluation_trace_bank_baseline_harness_artifacts()[0].to_dict()
        self.assertTrue(payload["behavior_safety_summary"]["no_paper_reproduction_claim"])
        self.assertTrue(payload["behavior_safety_summary"]["no_performance_claim"])
        for shell in payload["baseline_evaluation_harness_summary"]["per_policy_metric_shells"].values():
            self.assertEqual(shell["reward"]["status"], "schema_only_not_performance_claim")
            for episode in shell["per_episode_summary"]:
                self.assertFalse(episode["performance_claim"])


if __name__ == "__main__":
    unittest.main()
