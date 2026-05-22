from __future__ import annotations

import unittest

from src.analysis.exposure_matrix_review import build_exposure_matrix_report


class ExposureMatrixScopeGuardIntegrationTests(unittest.TestCase):
    def test_scope_flags_remain_true(self) -> None:
        report = build_exposure_matrix_report()
        payload = report.to_dict()
        self.assertTrue(payload["no_runtime_repair_performed"])
        self.assertTrue(payload["no_training_started"])
        self.assertTrue(payload["no_optimizer_step"])
        self.assertTrue(payload["no_replay_training"])
        self.assertTrue(payload["no_target_update_execution"])

    def test_no_runtime_policy_dependency_drift(self) -> None:
        report = build_exposure_matrix_report()
        payload = report.to_dict()
        self.assertTrue(payload["no_dependency_drift"])
        self.assertTrue(payload["no_environment_contract_drift"])
        self.assertTrue(payload["no_policy_drift"])
        self.assertTrue(payload["no_reward_timing_change"])
        self.assertTrue(payload["no_timeout_contract_drift"])
        self.assertTrue(payload["no_capacity_contract_drift"])
        self.assertTrue(payload["no_transmission_contract_drift"])
        self.assertTrue(payload["no_action_legality_drift"])

    def test_no_curve_fitting_or_paper_claim(self) -> None:
        report = build_exposure_matrix_report()
        payload = report.to_dict()
        self.assertTrue(payload["no_curve_fitting"])
        self.assertTrue(payload["no_simulator_output_tuning"])
        self.assertTrue(payload["no_paper_reproduction_claim"])


if __name__ == "__main__":
    unittest.main()
