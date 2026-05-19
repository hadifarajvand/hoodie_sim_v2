from __future__ import annotations

import unittest

from src.analysis.task_completion_lifecycle_formula_audit import CompletionLifecycleAuditConfig, CompletionLifecycleAuditReport, run_completion_lifecycle_audit


class TaskCompletionLifecycleSchemaUnitTests(unittest.TestCase):
    def test_report_schema_contains_required_fields(self) -> None:
        report = run_completion_lifecycle_audit(CompletionLifecycleAuditConfig())
        payload = report.to_dict()
        required = {
            "feature_id",
            "prerequisite_tags_verified",
            "prior_feature_gates_verified",
            "paper_default_runtime_verified",
            "formula_audit_summary",
            "hand_calculation_examples",
            "per_action_lifecycle_results",
            "lifecycle_breakpoint_summary",
            "completion_absence_diagnosis",
            "suspected_root_causes",
            "recommended_next_feature",
            "runtime_contracts_verified",
            "reward_timing_contract_verified",
            "pending_at_horizon_contract_verified",
            "no_training_started",
            "no_optimizer_step",
            "no_replay_training",
            "no_target_update_execution",
            "no_dependency_drift",
            "no_environment_contract_drift",
            "no_policy_drift",
            "no_reward_timing_change",
            "no_timeout_contract_drift",
            "no_capacity_contract_drift",
            "no_transmission_contract_drift",
            "no_curve_fitting",
            "no_simulator_output_tuning",
            "no_paper_reproduction_claim",
            "final_verdict",
        }
        self.assertTrue(required.issubset(payload))

    def test_report_requires_diagnostic_flags_to_be_true(self) -> None:
        with self.assertRaises(ValueError):
            CompletionLifecycleAuditReport(
                feature_id="043-task-completion-lifecycle-formula-audit",
                prerequisite_tags_verified=[],
                prior_feature_gates_verified=[],
                paper_default_runtime_verified={},
                formula_audit_summary={},
                hand_calculation_examples=[],
                per_action_lifecycle_results=[],
                lifecycle_breakpoint_summary={},
                completion_absence_diagnosis="x",
                suspected_root_causes=[],
                recommended_next_feature=None,
                runtime_contracts_verified={},
                reward_timing_contract_verified=True,
                pending_at_horizon_contract_verified=True,
                no_training_started=False,
                no_optimizer_step=True,
                no_replay_training=True,
                no_target_update_execution=True,
                no_dependency_drift=True,
                no_environment_contract_drift=True,
                no_policy_drift=True,
                no_reward_timing_change=True,
                no_timeout_contract_drift=True,
                no_capacity_contract_drift=True,
                no_transmission_contract_drift=True,
                no_curve_fitting=True,
                no_simulator_output_tuning=True,
                no_paper_reproduction_claim=True,
                final_verdict="prerequisite_blocked",
            )

    def test_report_rejects_failed_prerequisite_gates_and_prior_feature_gates(self) -> None:
        from src.analysis.task_completion_lifecycle_formula_audit.report import validate_prerequisite_evidence

        with self.assertRaises(ValueError):
            validate_prerequisite_evidence(
                [{"name": "branch", "verified": False, "details": "bad"}],
                [{"feature": "037", "verified": True, "details": "ok"}],
            )
        with self.assertRaises(ValueError):
            validate_prerequisite_evidence(
                [{"name": "branch", "verified": True, "details": "ok"}],
                [{"feature": "037", "verified": False, "details": "bad"}],
            )

    def test_dirty_pointer_only_keeps_no_unrelated_dirty_files_true(self) -> None:
        from src.analysis.task_completion_lifecycle_formula_audit import report as report_module

        original = report_module._tracked_dirty_paths
        try:
            report_module._tracked_dirty_paths = lambda: [".specify/feature.json"]  # type: ignore[assignment]
            tags = report_module.build_prerequisite_tags_verified()
            tag = next(item for item in tags if item["name"] == "no_unrelated_dirty_files")
            self.assertTrue(tag["verified"])
        finally:
            report_module._tracked_dirty_paths = original  # type: ignore[assignment]


if __name__ == "__main__":
    unittest.main()
