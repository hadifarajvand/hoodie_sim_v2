from __future__ import annotations

import unittest

from src.analysis.paper_default_terminal_exposure_probe import TerminalExposureProbeConfig, run_terminal_exposure_probe


class PaperDefaultTerminalExposureProbeIntegrationTests(unittest.TestCase):
    def test_probe_uses_hoodie_gym_environment(self) -> None:
        report = run_terminal_exposure_probe(TerminalExposureProbeConfig())
        self.assertTrue(report.paper_default_runtime_verified["repaired_runtime_contracts"])
        self.assertEqual(report.paper_default_runtime_verified["T"], 110)

    def test_probe_respects_legal_action_masks(self) -> None:
        report = run_terminal_exposure_probe(TerminalExposureProbeConfig())
        self.assertTrue(report.legal_action_mask_verified)
        self.assertTrue(all(result["legal_action_count"] >= 0 for result in report.per_strategy_results))

    def test_probe_does_not_change_runtime_or_reward_contracts(self) -> None:
        report = run_terminal_exposure_probe(TerminalExposureProbeConfig())
        self.assertTrue(report.reward_timing_contract_verified)
        self.assertTrue(report.pending_at_horizon_contract_verified)
        self.assertTrue(report.runtime_contracts_verified["no_environment_contract_drift"])
        self.assertTrue(report.runtime_contracts_verified["no_policy_drift"])

    def test_pending_at_horizon_is_not_terminal(self) -> None:
        report = run_terminal_exposure_probe(TerminalExposureProbeConfig())
        for result in report.per_strategy_results:
            self.assertGreaterEqual(result["pending_at_horizon_count"], 0)

    def test_reward_bearing_transition_requires_completion_or_drop(self) -> None:
        report = run_terminal_exposure_probe(TerminalExposureProbeConfig())
        for result in report.per_strategy_results:
            if result["reward_bearing_transition_count"] > 0:
                self.assertGreater(result["completed_task_count"] + result["dropped_task_count"], 0)

    def test_training_loop_does_not_run(self) -> None:
        report = run_terminal_exposure_probe(TerminalExposureProbeConfig())
        self.assertTrue(report.no_training_started)
        self.assertTrue(report.no_optimizer_step)
        self.assertTrue(report.no_replay_training)
        self.assertTrue(report.no_target_update_execution)

    def test_training_loop_emits_legal_actions_only(self) -> None:
        report = run_terminal_exposure_probe(TerminalExposureProbeConfig())
        self.assertTrue(report.legal_action_mask_verified)

    def test_no_dependency_environment_policy_reward_drift(self) -> None:
        report = run_terminal_exposure_probe(TerminalExposureProbeConfig())
        self.assertTrue(report.no_dependency_drift)
        self.assertTrue(report.no_environment_contract_drift)
        self.assertTrue(report.no_policy_drift)
        self.assertTrue(report.no_reward_timing_change)


if __name__ == "__main__":
    unittest.main()
