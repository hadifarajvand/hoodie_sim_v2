from __future__ import annotations

import json
from pathlib import Path
import unittest

from src.analysis.reward_equation_terminal_reward_contract.report import build_reward_contract_report, write_reward_contract_report


class RewardEquationTerminalRewardContractReportIntegrationTest(unittest.TestCase):
    def test_report_writes_deterministically(self) -> None:
        report = build_reward_contract_report()
        json_path, markdown_path = write_reward_contract_report(report)

        self.assertTrue(json_path.exists())
        self.assertTrue(markdown_path.exists())

        payload = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["feature_id"], "029-reward-equation-terminal-reward-contract")
        self.assertIn("recovered_equations", payload)
        self.assertIn("success_reward_contract", payload)
        self.assertIn("final_verdict", payload)
        self.assertEqual(payload["final_verdict"], "paper_backed_with_assumption_backed_aggregation")

    def test_report_contains_required_schema_fields(self) -> None:
        payload = build_reward_contract_report().to_dict()
        required = {
            "feature_id",
            "schema_version",
            "source_gates",
            "recovered_equations",
            "success_reward_contract",
            "drop_penalty_contract",
            "no_task_reward_contract",
            "delay_cost_contract",
            "terminal_timing_contract",
            "aggregation_contract",
            "runtime_audit",
            "traceability_audit",
            "mismatch_findings",
            "repaired_items",
            "unrecoverable_items",
            "assumption_backed_items",
            "tests_or_validation_commands",
            "no_training_or_policy_drift",
            "no_dependency_drift",
            "final_verdict",
        }
        self.assertTrue(required.issubset(payload.keys()))


if __name__ == "__main__":
    unittest.main()
