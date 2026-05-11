from __future__ import annotations

import unittest

from src.analysis.reward_equation_terminal_reward_contract.reward_evidence import build_reward_evidence_summary


class RewardEquationTerminalRewardContractRecoveryTest(unittest.TestCase):
    def test_equation_recovery_contains_normalized_fields(self) -> None:
        summary = build_reward_evidence_summary()
        equations = {item["equation_id"]: item for item in summary["equations"]}
        self.assertEqual(equations["20"]["recovery_status"], "paper_backed")
        self.assertIn("no task", equations["20"]["raw_ocr_text"])
        self.assertIn("Phi_n^priv(t)", equations["22"]["normalized_formula"])
        self.assertEqual(equations["23"]["recovery_status"], "paper_backed_with_ocr_noise_caveat")
        self.assertIn("arg max", equations["24"]["normalized_formula"])

    def test_c_value_is_recovered_and_classified(self) -> None:
        summary = build_reward_evidence_summary()
        self.assertEqual(summary["c_value"]["value"], 40)
        self.assertTrue(summary["c_value"]["artifact_backed"])
        self.assertEqual(summary["c_value"]["recovery_status"], "paper_backed")


if __name__ == "__main__":
    unittest.main()
