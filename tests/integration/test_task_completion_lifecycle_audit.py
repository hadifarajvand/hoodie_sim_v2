from __future__ import annotations

import unittest

from src.analysis.task_completion_lifecycle_formula_audit import CompletionLifecycleAuditConfig, run_completion_lifecycle_audit


class TaskCompletionLifecycleAuditIntegrationTests(unittest.TestCase):
    def test_audit_uses_hoodie_gym_environment_and_legal_masks(self) -> None:
        report = run_completion_lifecycle_audit(CompletionLifecycleAuditConfig())
        self.assertEqual(report.feature_id, "043-task-completion-lifecycle-formula-audit")
        self.assertTrue(all(result["counters"]["legal_action_count"] >= 0 for result in report.per_action_lifecycle_results))
        self.assertTrue(report.reward_timing_contract_verified)
        self.assertTrue(report.pending_at_horizon_contract_verified)

    def test_audit_is_deterministic_for_repeated_runs(self) -> None:
        first = run_completion_lifecycle_audit(CompletionLifecycleAuditConfig()).to_dict()
        second = run_completion_lifecycle_audit(CompletionLifecycleAuditConfig()).to_dict()
        self.assertEqual(first["formula_audit_summary"], second["formula_audit_summary"])
        self.assertEqual(first["hand_calculation_examples"], second["hand_calculation_examples"])


if __name__ == "__main__":
    unittest.main()
