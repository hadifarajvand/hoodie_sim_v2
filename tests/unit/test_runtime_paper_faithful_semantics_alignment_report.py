from __future__ import annotations

import unittest

from src.analysis.runtime_paper_faithful_semantics_alignment.report import build_feature_071_report


class RuntimePaperFaithfulSemanticsAlignmentReportTests(unittest.TestCase):
    def test_report_contains_required_evidence_and_is_passed(self) -> None:
        report = build_feature_071_report()
        payload = report.to_dict()
        self.assertEqual(payload["feature_name"], "Feature 071 - Runtime Paper-Faithful Semantics Alignment")
        self.assertEqual(payload["status"], "runtime_paper_faithful_semantics_alignment_ready")
        self.assertTrue(payload["passed"])
        self.assertIn("deadline_evidence", payload)
        self.assertIn("terminal_state_evidence", payload)
        self.assertIn("reward_runtime_evidence", payload)
        self.assertIn("compatibility_evidence", payload)
        self.assertTrue(payload["deadline_evidence"]["paper_mode_default"])
        self.assertTrue(payload["deadline_evidence"]["compatibility_mode_explicit"])
        self.assertTrue(payload["compatibility_evidence"]["build_timeout_contract_default_is_paper"])
        self.assertTrue(payload["compatibility_evidence"]["build_timeout_contract_compatibility_is_explicit"])
        self.assertTrue(payload["compatibility_evidence"]["deadline_rules_default_is_paper"])
        self.assertTrue(payload["compatibility_evidence"]["deadline_rules_compatibility_is_explicit"])
        self.assertTrue(payload["compatibility_evidence"]["reward_for_terminal_task_default_is_paper"])
        self.assertTrue(payload["compatibility_evidence"]["reward_for_terminal_task_compatibility_is_explicit"])
        self.assertTrue(payload["terminal_state_evidence"]["pending_cannot_emit_reward"])
        self.assertEqual(payload["reward_runtime_evidence"]["equation_22_private_example_phi"], 4)
        self.assertEqual(payload["reward_runtime_evidence"]["equation_23_public_example_phi"], 5)
        self.assertEqual(payload["reward_runtime_evidence"]["reward_for_terminal_task_default_completion_reward"], -4.0)
        self.assertEqual(payload["reward_runtime_evidence"]["reward_for_terminal_task_compatibility_completion_reward"], -3.0)
        self.assertTrue(payload["reward_runtime_evidence"]["reward_for_terminal_task_default_uses_plus_one"])
        self.assertTrue(payload["reward_runtime_evidence"]["reward_for_terminal_task_compatibility_preserves_old_approximation"])
        self.assertEqual(payload["reward_runtime_evidence"]["reward_slot_convention"], "reward_slot_for_terminal emits at terminal_slot + 1")
        self.assertTrue(payload["feature_068r_regression_status"]["passed"])
        self.assertTrue(payload["feature_069_regression_status"]["passed"])
        self.assertTrue(payload["feature_070_regression_status"]["passed"])
        self.assertIn("Feature 072", payload["paper_claim_boundary"])
        self.assertIn("No full paper reproduction claim", payload["paper_claim_boundary"])
        self.assertIn("Feature 072", payload["recommended_next_feature"])

    def test_report_rejects_full_paper_claim_and_requires_ready_status(self) -> None:
        report = build_feature_071_report()
        self.assertNotIn("full paper reproduction is claimed", report.paper_claim_boundary)
        self.assertEqual(report.status, "runtime_paper_faithful_semantics_alignment_ready")


if __name__ == "__main__":
    unittest.main()
