from __future__ import annotations

import unittest

from src.analysis.selected_action_outcome_evidence_rerun import build_selected_action_outcome_evidence_rerun_report


class SelectedActionOutcomeEvidenceRerunScopeGuardTest(unittest.TestCase):
    def test_no_runtime_policy_dependency_training_drift(self) -> None:
        payload = build_selected_action_outcome_evidence_rerun_report().to_dict()
        for key in [
            "no_runtime_repair_performed",
            "no_training_started",
            "no_optimizer_step",
            "no_replay_training",
            "no_target_update_execution",
            "no_dependency_drift",
            "no_policy_drift",
            "no_reward_timing_change",
            "no_timeout_contract_drift",
            "no_capacity_contract_drift",
            "no_transmission_contract_drift",
            "no_action_legality_drift",
            "no_action_selection_drift",
            "no_curve_fitting",
            "no_simulator_output_tuning",
            "no_paper_reproduction_claim",
        ]:
            self.assertTrue(payload[key])


if __name__ == "__main__":
    unittest.main()
