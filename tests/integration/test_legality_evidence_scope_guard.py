from __future__ import annotations

import unittest

from src.analysis.legality_evidence_expansion import build_legality_evidence_report


class LegalityEvidenceScopeGuardIntegrationTests(unittest.TestCase):
    def test_scope_guard_flags_are_explicit(self) -> None:
        payload = build_legality_evidence_report().to_dict()
        self.assertTrue(payload["no_runtime_repair_performed"])
        self.assertTrue(payload["no_training_started"])
        self.assertTrue(payload["no_optimizer_step"])
        self.assertTrue(payload["no_replay_training"])
        self.assertTrue(payload["no_target_update_execution"])
        self.assertTrue(payload["no_dependency_drift"])
        self.assertTrue(payload["no_policy_drift"])
        self.assertTrue(payload["no_reward_timing_change"])
        self.assertTrue(payload["no_timeout_contract_drift"])
        self.assertTrue(payload["no_capacity_contract_drift"])
        self.assertTrue(payload["no_transmission_contract_drift"])
        self.assertTrue(payload["no_action_legality_drift"])
        self.assertTrue(payload["no_action_selection_drift"])
        self.assertTrue(payload["no_curve_fitting"])
        self.assertTrue(payload["no_simulator_output_tuning"])
        self.assertTrue(payload["no_paper_reproduction_claim"])


if __name__ == "__main__":
    unittest.main()
