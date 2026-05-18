from __future__ import annotations

import unittest

from src.analysis.paper_default_terminal_exposure_probe import TerminalExposureProbeConfig, TerminalExposureReport, run_terminal_exposure_probe


class PaperDefaultTerminalExposureSchemaUnitTests(unittest.TestCase):
    def test_terminal_exposure_counter_schema_exact(self) -> None:
        report = run_terminal_exposure_probe(TerminalExposureProbeConfig())
        first = report.per_strategy_results[0]
        expected = {
            "episode_count",
            "episode_length",
            "seed",
            "generated_task_count",
            "exposed_decision_count",
            "selected_action_count",
            "legal_action_count",
            "illegal_action_count",
            "local_action_count",
            "horizontal_action_count",
            "vertical_action_count",
            "admitted_task_count",
            "transmission_started_count",
            "transmission_completed_count",
            "execution_started_count",
            "execution_completed_count",
            "completed_task_count",
            "dropped_task_count",
            "terminal_transition_count",
            "reward_bearing_transition_count",
            "pending_at_horizon_count",
            "terminal_transition_ratio",
            "reward_bearing_transition_ratio",
            "pending_at_horizon_ratio",
            "max_observed_task_age_slots",
            "max_queue_wait_slots",
            "deadline_reached_count",
            "deadline_expired_count",
            "reward_emitted_count",
            "nan_or_omitted_reward_count",
            "terminal_outcome_by_action_type",
            "pending_by_action_type",
            "lifecycle_trace_integrity_verified",
            "strategy",
        }
        self.assertEqual(set(first), expected)

    def test_report_schema_and_final_verdict(self) -> None:
        report = run_terminal_exposure_probe(TerminalExposureProbeConfig())
        payload = report.to_dict()
        required = {
            "feature_id",
            "prerequisite_tags_verified",
            "prior_feature_gates_verified",
            "paper_default_runtime_verified",
            "probe_config",
            "probe_strategies",
            "per_strategy_results",
            "aggregate_terminal_exposure_summary",
            "reward_timing_contract_verified",
            "pending_at_horizon_contract_verified",
            "legal_action_mask_verified",
            "runtime_contracts_verified",
            "diagnosis",
            "recommended_next_feature",
            "no_training_started",
            "no_optimizer_step",
            "no_replay_training",
            "no_target_update_execution",
            "no_dependency_drift",
            "no_environment_contract_drift",
            "no_policy_drift",
            "no_reward_timing_change",
            "no_curve_fitting",
            "no_simulator_output_tuning",
            "no_paper_reproduction_claim",
            "final_verdict",
        }
        self.assertTrue(required.issubset(payload))
        self.assertTrue(payload["no_training_started"])
        self.assertTrue(payload["no_optimizer_step"])
        self.assertTrue(payload["no_replay_training"])
        self.assertTrue(payload["no_target_update_execution"])
        self.assertTrue(payload["no_dependency_drift"])
        self.assertTrue(payload["no_environment_contract_drift"])
        self.assertTrue(payload["no_policy_drift"])
        self.assertTrue(payload["no_reward_timing_change"])
        self.assertTrue(payload["no_curve_fitting"])
        self.assertTrue(payload["no_simulator_output_tuning"])
        self.assertTrue(payload["no_paper_reproduction_claim"])
        self.assertIn(payload["final_verdict"], {"terminal_exposure_present", "terminal_exposure_absent_under_paper_default"})

    def test_report_rejects_false_audit_flags(self) -> None:
        with self.assertRaises(ValueError):
            TerminalExposureReport(
                feature_id="042-paper-default-terminal-exposure-probe",
                prerequisite_tags_verified=[],
                prior_feature_gates_verified=[],
                paper_default_runtime_verified={},
                probe_config={},
                probe_strategies=[],
                per_strategy_results=[],
                aggregate_terminal_exposure_summary={},
                reward_timing_contract_verified=True,
                pending_at_horizon_contract_verified=True,
                legal_action_mask_verified=True,
                runtime_contracts_verified={},
                diagnosis="x",
                recommended_next_feature=None,
                no_training_started=False,
                no_optimizer_step=True,
                no_replay_training=True,
                no_target_update_execution=True,
                no_dependency_drift=True,
                no_environment_contract_drift=True,
                no_policy_drift=True,
                no_reward_timing_change=True,
                no_curve_fitting=True,
                no_simulator_output_tuning=True,
                no_paper_reproduction_claim=True,
                final_verdict="prerequisite_blocked",
            )

    def test_no_training_optimizer_replay_target_update(self) -> None:
        report = run_terminal_exposure_probe(TerminalExposureProbeConfig())
        self.assertTrue(report.no_training_started)
        self.assertTrue(report.no_optimizer_step)
        self.assertTrue(report.no_replay_training)
        self.assertTrue(report.no_target_update_execution)

    def test_no_dependency_environment_policy_reward_drift(self) -> None:
        report = run_terminal_exposure_probe(TerminalExposureProbeConfig())
        self.assertTrue(report.no_dependency_drift)
        self.assertTrue(report.no_environment_contract_drift)
        self.assertTrue(report.no_policy_drift)
        self.assertTrue(report.no_reward_timing_change)

    def test_no_curve_fitting_or_reproduction_claim(self) -> None:
        report = run_terminal_exposure_probe(TerminalExposureProbeConfig())
        self.assertTrue(report.no_curve_fitting)
        self.assertTrue(report.no_simulator_output_tuning)
        self.assertTrue(report.no_paper_reproduction_claim)


if __name__ == "__main__":
    unittest.main()
