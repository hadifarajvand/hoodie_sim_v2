from __future__ import annotations

import unittest

from src.analysis.exposure_matrix_review import ExposureDecisionRecord, ExposureMatrixConfig, build_exposure_matrix_report


class ExposureMatrixSchemaUnitTests(unittest.TestCase):
    def test_config_uses_paper_default_grid(self) -> None:
        config = ExposureMatrixConfig()
        self.assertEqual(config.feature_id, "047-exposure-matrix-review")
        self.assertEqual(config.episode_length, 110)
        self.assertEqual(config.timeout_slots, 20)
        self.assertEqual(config.node_count, 20)
        self.assertEqual(config.arrival_probability, 0.5)
        self.assertEqual(list(config.seeds), [0, 1, 2])
        self.assertEqual(
            config.strategies,
            (
                "environment_default_policy_probe",
                "force_local_legal_probe",
                "force_horizontal_legal_probe",
                "force_vertical_legal_probe",
                "mixed_legal_round_robin_probe",
            ),
        )
        self.assertTrue(config.no_runtime_repair)
        self.assertTrue(config.no_training)

    def test_exposure_decision_record_schema(self) -> None:
        record = ExposureDecisionRecord(
            run_id="environment_default_policy_probe:0",
            strategy="environment_default_policy_probe",
            seed=0,
            decision_opportunity_index=1,
            generated_task_id="task-1",
            admitted_slot=0,
            selected_action="local",
            legal_local=True,
            legal_horizontal=False,
            legal_vertical=False,
            selected_was_legal=True,
            destination="self",
            queue_type="private",
            terminal_outcome="completed",
            reward_available=False,
            pending_at_horizon=False,
            task_age_slots=0,
            wait_slots=0,
            execution_progress_slots=1,
            transmission_delay_slots=None,
            evidence_source="trace",
        )
        payload = record.to_dict()
        self.assertEqual(payload["selected_action"], "local")
        self.assertIn("legal_local", payload)
        self.assertIn("legal_horizontal", payload)
        self.assertIn("legal_vertical", payload)
        self.assertIn("selected_was_legal", payload)
        self.assertIn("selected_action_available", payload)

    def test_report_schema_exact_fields(self) -> None:
        report = build_exposure_matrix_report()
        payload = report.to_dict()
        self.assertEqual(
            set(payload),
            {
                "feature_id",
                "prerequisite_tags_verified",
                "prior_feature_gates_verified",
                "paper_default_runtime_verified",
                "exposure_matrix_input_sources",
                "exposure_matrix_population",
                "legal_action_evidence_source",
                "legal_action_evidence_coverage_ratio",
                "per_strategy_seed_matrix",
                "aggregate_exposure_matrix",
                "per_action_outcome_matrix",
                "per_queue_matrix",
                "offload_exposure_matrix",
                "illegal_action_summary",
                "exposure_bias_summary",
                "load_vs_exposure_summary",
                "matrix_completeness_summary",
                "dominant_exposure_findings",
                "diagnosis",
                "recommended_next_feature",
                "no_runtime_repair_performed",
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
                "no_action_legality_drift",
                "no_curve_fitting",
                "no_simulator_output_tuning",
                "no_paper_reproduction_claim",
                "final_verdict",
            },
        )
        self.assertIn("selected_illegal_action_count", payload["aggregate_exposure_matrix"])
        self.assertIn("selected_illegal_action_count", payload["per_strategy_seed_matrix"][0])
        self.assertIn("evidence_status", payload["illegal_action_summary"])


if __name__ == "__main__":
    unittest.main()
