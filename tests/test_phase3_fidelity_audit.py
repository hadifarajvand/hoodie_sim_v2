from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from phase3_fidelity_audit import (
    _classify_action_contract,
    _classify_lstm_contract,
    _classify_reward_contract,
    _classify_state_contract,
    _classify_training_loop_contract,
    _make_summary,
    run_audit,
)


class Phase3FidelityAuditTests(unittest.TestCase):
    def test_state_summary_has_expected_failures(self):
        rows = _classify_state_contract()
        summary = _make_summary(rows)
        self.assertEqual(summary["overall_status"], "FAIL")
        self.assertGreaterEqual(summary["counts"]["FAIL"], 1)

    def test_action_summary_passes(self):
        summary = _make_summary(_classify_action_contract())
        self.assertEqual(summary["overall_status"], "PARTIAL")

    def test_reward_and_lstm_include_failures(self):
        self.assertEqual(_make_summary(_classify_reward_contract())["overall_status"], "FAIL")
        self.assertEqual(_make_summary(_classify_lstm_contract())["overall_status"], "FAIL")

    def test_training_loop_is_partial(self):
        summary = _make_summary(_classify_training_loop_contract())
        self.assertEqual(summary["overall_status"], "FAIL")

    def test_audit_writes_report_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "audit"
            report = run_audit(out_dir)
            self.assertEqual(report["audit_phase"], "Phase 3.0")
            self.assertFalse(report["runtime_behavior_changed"])
            self.assertFalse(report["paper_performance_claims_made"])
            for name in [
                "phase3_fidelity_report.json",
                "phase3_fidelity_report.md",
                "state_contract_gap_matrix.csv",
                "action_contract_gap_matrix.csv",
                "reward_contract_gap_matrix.csv",
                "lstm_contract_gap_matrix.csv",
                "training_loop_gap_matrix.csv",
            ]:
                self.assertTrue((out_dir / name).exists(), name)


if __name__ == "__main__":
    unittest.main()
