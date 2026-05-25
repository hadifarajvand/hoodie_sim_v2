from __future__ import annotations

import unittest

from src.analysis.real_torch_trainer_binding_audit import build_real_torch_trainer_binding_audit_report


class RealTorchTrainerBindingAuditMetricsTests(unittest.TestCase):
    def test_torch_and_torchrl_environment_are_not_ignored(self) -> None:
        payload = build_real_torch_trainer_binding_audit_report().to_dict()
        torch_summary = payload["torch_availability_summary"]
        self.assertTrue(torch_summary["torch_find_spec_available"])
        self.assertTrue(torch_summary["torchrl_find_spec_available"])
        self.assertTrue(torch_summary["torch_import_available"])
        self.assertEqual(torch_summary["torch_version"], "2.12.0")
        self.assertTrue(torch_summary["torch_pip_show_present"])
        self.assertTrue(torch_summary["torchrl_pip_show_present"])
        self.assertTrue(payload["binding_audit_summary"]["environment_supports_real_binding"])

    def test_feature_060_pass_claim_is_compared_to_binding_evidence(self) -> None:
        payload = build_real_torch_trainer_binding_audit_report().to_dict()
        self.assertTrue(payload["feature_060_claim_summary"]["feature_060_claims_campaign_execution_passed"])
        self.assertFalse(payload["binding_audit_summary"]["feature_060_claim_supported"])
        self.assertIn("feature_060_claim_not_supported_by_real_trainer_binding", payload["remaining_blockers"])

    def test_scalar_fallback_markers_are_detected(self) -> None:
        payload = build_real_torch_trainer_binding_audit_report().to_dict()
        fallback = payload["simulation_fallback_summary"]
        self.assertTrue(fallback["random_random_used"])
        self.assertTrue(fallback["manual_replay_list_construction"])
        self.assertTrue(fallback["manual_scalar_loss_calculation"])
        self.assertTrue(fallback["manual_optimizer_step_count_increment"])
        self.assertTrue(fallback["manual_target_sync_count_calculation"])
        self.assertTrue(fallback["torch_tensor_module_optimizer_absent"])
        self.assertTrue(fallback["scalar_fallback_detected"])

    def test_missing_binding_evidence_is_named_exactly(self) -> None:
        payload = build_real_torch_trainer_binding_audit_report().to_dict()
        for blocker in (
            "feature_060_runner_missing_torch_import",
            "feature_060_runner_missing_torchrl_import",
            "feature_060_runner_missing_real_trainer_import",
            "feature_060_runner_missing_real_trainer_instantiation",
            "feature_060_runner_missing_real_trainer_update_fit_train_call",
            "feature_060_runner_uses_scalar_fallback_campaign",
        ):
            self.assertIn(blocker, payload["remaining_blockers"])


if __name__ == "__main__":
    unittest.main()
