from __future__ import annotations

import unittest

from src.analysis.training_foundation_contract import (
    ActionIndexContract,
    CheckpointSchema,
    ReplayTransitionSchema,
    SeedProtocol,
    StateContract,
    TargetUpdateFrequencyContract,
    TrainEvalSplitProtocol,
    build_training_foundation_report,
)


class TrainingFoundationReadinessGateIntegrationTests(unittest.TestCase):
    def test_terminal_outcome_exposure_gate_blocks_training_when_terminal_ratio_insufficient(self) -> None:
        report = build_training_foundation_report(
            prerequisite_tags_verified=[{"tag": "037-baseline-revalidation-after-runtime-repair-complete", "commit": "69debe2f3c75e5cfe2e059c49e1063156c00130e"}],
            state_contract=StateContract(
                version="1.0",
                agent_key_field="edge_agent_id",
                field_order=["queue_length", "queue_delay"],
                field_types={"queue_length": "int", "queue_delay": "float"},
                normalization_rules={},
                missing_value_encoding={"no_task": 0},
                history_buffer_policy="separate_history_buffer",
                lookback_w=10,
                observable_only=True,
                diagnostics_excluded_from_model_input=True,
                no_privileged_future_information=True,
            ),
            action_index_contract=ActionIndexContract(
                version="1.0",
                action_to_semantics={0: "local", 1: "horizontal", 2: "vertical_cloud"},
                horizontal_resolution_rule="helper_resolves_approved_neighbor",
                vertical_cloud_independent_rule="vertical_cloud_independent_of_figure7_adjacency",
                illegal_action_behavior="explicitly_rejected_or_masked",
                mask_surface="separate_metadata",
            ),
            replay_schema=ReplayTransitionSchema(
                version="1.0",
                fields=["state_t", "action_index", "action_semantics", "legal_action_mask_t", "reward_t_plus_k", "reward_available", "next_state", "done", "truncated", "task_id", "source_agent_id", "selected_destination", "arrival_slot", "decision_slot", "terminal_slot", "terminal_outcome", "delay_slots", "seed", "trace_id", "episode_id", "runtime_contract_version"],
                delayed_reward_policy="reward_available_false_until_terminal",
                pending_at_horizon_policy="explicit_pending_at_horizon",
                no_fake_terminal_samples=True,
            ),
            target_update_frequency_contract=TargetUpdateFrequencyContract(
                update_frequency=2000,
                iteration_unit="environment_step",
                iteration_unit_status="explicit",
                candidate_meanings=["environment_step", "optimization_step", "replay_insertion", "gradient_update"],
                training_use_allowed=False,
            ),
            seed_protocol=SeedProtocol(
                version="1.0",
                training_trace_generation_seed=11,
                evaluation_trace_generation_seed=13,
                replay_sampling_seed=17,
                model_initialization_seed=19,
                action_exploration_seed=23,
                python_seeded_now=True,
                numpy_seeded_now=True,
                torch_seed_future_required=True,
                recorded_in_artifacts=True,
            ),
            train_eval_split_protocol=TrainEvalSplitProtocol(
                version="1.0",
                training_trace_ids=["train-a"],
                evaluation_trace_ids=["eval-a"],
                fixed_evaluation_trace_bank=True,
                explicit_trace_ids=True,
                no_evaluation_on_training_traces=True,
                no_unfair_baseline_hoodie_trace_mismatch=True,
            ),
            checkpoint_schema=CheckpointSchema(
                feature_id="038-training-foundation-contract",
                commit_sha="abc123",
                config_path="configs/training_foundation.yaml",
                config_hash="deadbeef",
                state_contract_version="1.0",
                action_contract_version="1.0",
                replay_schema_version="1.0",
                seed_bundle={"training_trace_generation_seed": 11, "evaluation_trace_generation_seed": 13, "replay_sampling_seed": 17, "model_initialization_seed": 19, "action_exploration_seed": 23},
                training_step_counters={"environment_steps": 0, "optimization_steps": 0},
                target_update_counter=0,
                runtime_contract_refs=["Feature 032", "Feature 033"],
                paper_default_parameter_refs=["paper_default"],
                metadata_only=True,
                no_actual_model_checkpoint=True,
            ),
            generated_arrivals=1000,
            decisions_exposed=950,
            finalized_terminal_tasks=2,
            completed_tasks=1,
            dropped_tasks=1,
            pending_at_horizon=948,
            per_policy_smoke_statistics=[{"policy": "random", "sample_size": 5}],
            runtime_contracts_verified=["Feature 032", "Feature 033"],
            threshold_approved=False,
        )
        gate = report.terminal_outcome_exposure_gate
        self.assertTrue(gate.training_blocked)
        self.assertEqual(gate.threshold_status, "pending_user_approval")
        self.assertEqual(gate.finalized_terminal_tasks, 2)
        self.assertEqual(gate.completed_tasks + gate.dropped_tasks, gate.finalized_terminal_tasks)
        self.assertGreater(gate.pending_transition_ratio, 0.0)
        self.assertGreater(gate.reward_bearing_transition_ratio, 0.0)


if __name__ == "__main__":
    unittest.main()
