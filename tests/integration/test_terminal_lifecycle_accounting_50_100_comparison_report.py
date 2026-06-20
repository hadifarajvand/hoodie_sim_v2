from __future__ import annotations

import json
import unittest
from pathlib import Path

from src.analysis.terminal_lifecycle_accounting_50_100_comparison.config import REPORT_JSON, REPORT_MD

from tests.integration.test_terminal_lifecycle_accounting_50_100_comparison import run_fake_pipeline


class TerminalLifecycleAccounting50_100ComparisonReportTests(unittest.TestCase):
    def test_report_files_include_required_decisions(self) -> None:
        payload = run_fake_pipeline()
        report = json.loads(Path(REPORT_JSON).read_text(encoding="utf-8"))
        self.assertEqual(report["final_verdict"], "terminal_lifecycle_50_100_comparison_ready")
        self.assertEqual(report["diagnostic_decision"]["recommended_next_action"], "fix_completion_path_next")
        self.assertTrue(report["claim_safety_status"]["claim_safety_passed"])
        self.assertFalse(report["paper_reproduction_claim_made"])
        self.assertFalse(report["performance_superiority_claim_made"])
        self.assertFalse(report["baseline_superiority_claim_made"])
        self.assertEqual(report["checkpoint_budgets"], [50, 100])
        self.assertEqual(report["training_mode"], "cumulative_staged_50_100_comparison")
        self.assertTrue(report["raw_vs_canonical_terminal_reconciliation"]["overall"]["terminal_reconciled"])
        self.assertTrue(Path(REPORT_MD).exists())
        self.assertEqual(payload["final_verdict"], "terminal_lifecycle_50_100_comparison_ready")


if __name__ == "__main__":
    unittest.main()
