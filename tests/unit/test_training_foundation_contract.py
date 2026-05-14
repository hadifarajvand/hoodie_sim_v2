from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.analysis.training_foundation_contract import (
    ActionIndexContract,
    CheckpointSchema,
    ReplayTransitionSchema,
    SeedProtocol,
    StateContract,
    TargetUpdateFrequencyContract,
    TerminalOutcomeExposureGate,
    TrainEvalSplitProtocol,
    build_training_foundation_report,
    write_training_foundation_report,
)


class TrainingFoundationContractUnitTests(unittest.TestCase):
    def _state_contract(self) -> StateContract:
        return StateContract(
            version="1.0",
            agent_key_field="edge_agent_id",
            field_order=["queue_length", "queue_delay", "available_capacity"],
            field_types={
                "queue_length": "int",
                "queue_delay": "float",
                "available_capacity": "float",
            },
            normalization_rules={"queue_delay": "divide_by_slot_duration"},
            missing_value_encoding={"no_task": 0},
            history_buffer_policy="separate_history_buffer",
            lookback_w=10,
            observable_only=True,
            diagnostics_excluded_from_model_input=True,
            no_privileged_future_information=True,
        )

    def _action_contract(self) -> ActionIndexContract:
        return ActionIndexContract(
            version="1.0",
            action_to_semantics={0: "local", 1: "horizontal", 2: "vertical_cloud"},
            horizontal_resolution_rule="helper_resolves_approved_neighbor",
            vertical_cloud_independent_rule="vertical_cloud_independent_of_figure7_adjacency",
            illegal_action_behavior="explicitly_rejected_or_masked",
            mask_surface="separate_metadata",
        )

    def _replay_schema(self) -> ReplayTransitionSchema:
        return ReplayTransitionSchema(
            version="1.0",
            fields=[
                "state_t",
                "action_index",
                "action_semantics",
                "legal_action_mask_t",
                "reward_t_plus_k",
                "reward_available",
                "next_state",
                "done",
                "truncated",
                "task_id",
                "source_agent_id",
                "selected_destination",
                "arrival_slot",
                "decision_slot",
                "terminal_slot",
                "terminal_outcome",
                "delay_slots",
                "seed",
                "trace_id",
                "episode_id",
                "runtime_contract_version",
            ],
            delayed_reward_policy="reward_available_false_until_terminal",
            pending_at_horizon_policy="explicit_pending_at_horizon",
            no_fake_terminal_samples=True,
        )

    def _target_contract(self) -> TargetUpdateFrequencyContract:
        return TargetUpdateFrequencyContract(
            update_frequency=2000,
            iteration_unit=None,
            iteration_unit_status="unresolved_pending_user_approval",
            candidate_meanings=["environment_step", "optimization_step", "replay_insertion", "gradient_update"],
            training_use_allowed=False,
        )

    def _seed_protocol(self) -> SeedProtocol:
        return SeedProtocol(
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
        )

    def _split_protocol(self) -> TrainEvalSplitProtocol:
        return TrainEvalSplitProtocol(
            version="1.0",
            training_trace_ids=["train-a", "train-b"],
            evaluation_trace_ids=["eval-a"],
            fixed_evaluation_trace_bank=True,
            explicit_trace_ids=True,
            no_evaluation_on_training_traces=True,
            no_unfair_baseline_hoodie_trace_mismatch=True,
        )

    def _checkpoint_schema(self) -> CheckpointSchema:
        return CheckpointSchema(
            feature_id="038-training-foundation-contract",
            commit_sha={"required": True, "type": "git_commit_sha", "source": "checkpoint_creation"},
            config_path={"required": True, "type": "filesystem_path", "source": "checkpoint_creation"},
            config_hash={"required": True, "type": "content_hash", "source": "checkpoint_creation"},
            state_contract_version="1.0",
            action_contract_version="1.0",
            replay_schema_version="1.0",
            seed_bundle={
                "training_trace_generation_seed": 11,
                "evaluation_trace_generation_seed": 13,
                "replay_sampling_seed": 17,
                "model_initialization_seed": 19,
                "action_exploration_seed": 23,
            },
            training_step_counters={"environment_steps": 0, "optimization_steps": 0},
            target_update_counter=0,
            runtime_contract_refs=["Feature 032", "Feature 033", "Feature 034", "Feature 035", "Feature 036", "Feature 037"],
            paper_default_parameter_refs=["paper_default"],
            metadata_only=True,
            no_actual_model_checkpoint=True,
        )

    def test_state_contract_has_stable_field_order(self) -> None:
        contract = self._state_contract()
        self.assertEqual(
            list(StateContract.__dataclass_fields__),
            [
                "version",
                "agent_key_field",
                "field_order",
                "field_types",
                "normalization_rules",
                "missing_value_encoding",
                "history_buffer_policy",
                "lookback_w",
                "observable_only",
                "diagnostics_excluded_from_model_input",
                "no_privileged_future_information",
            ],
        )
        self.assertTrue(contract.observable_only)
        self.assertTrue(contract.diagnostics_excluded_from_model_input)
        self.assertTrue(contract.no_privileged_future_information)
        self.assertEqual(contract.lookback_w, 10)

    def test_action_index_contract_is_stable_and_mask_aware(self) -> None:
        contract = self._action_contract()
        self.assertEqual(contract.action_to_semantics[1], "horizontal")
        self.assertEqual(contract.horizontal_resolution_rule, "helper_resolves_approved_neighbor")
        self.assertEqual(contract.vertical_cloud_independent_rule, "vertical_cloud_independent_of_figure7_adjacency")
        self.assertEqual(contract.mask_surface, "separate_metadata")
        self.assertIn("masked", contract.illegal_action_behavior)

    def test_replay_schema_supports_delayed_rewards(self) -> None:
        contract = self._replay_schema()
        self.assertIn("reward_available", contract.fields)
        self.assertTrue(contract.no_fake_terminal_samples)
        self.assertEqual(contract.delayed_reward_policy, "reward_available_false_until_terminal")

    def test_replay_schema_marks_pending_at_horizon_explicitly(self) -> None:
        contract = self._replay_schema()
        self.assertEqual(contract.pending_at_horizon_policy, "explicit_pending_at_horizon")
        self.assertIn("terminal_outcome", contract.fields)

    def test_target_update_frequency_contract_records_2000_iterations(self) -> None:
        contract = self._target_contract()
        self.assertEqual(contract.update_frequency, 2000)
        self.assertIsNone(contract.iteration_unit)
        self.assertEqual(contract.iteration_unit_status, "unresolved_pending_user_approval")
        self.assertFalse(contract.training_use_allowed)

    def test_target_update_frequency_iteration_unit_is_explicit_or_unresolved(self) -> None:
        unresolved = self._target_contract()
        self.assertEqual(unresolved.iteration_unit_status, "unresolved_pending_user_approval")
        self.assertIsNone(unresolved.iteration_unit)
        self.assertFalse(unresolved.training_use_allowed)
        self.assertIn("optimization_step", unresolved.candidate_meanings)

        unresolved = TargetUpdateFrequencyContract(
            update_frequency=2000,
            iteration_unit="environment_step",
            iteration_unit_status="explicit_user_approved",
            candidate_meanings=self._target_contract().candidate_meanings,
            training_use_allowed=False,
        )
        self.assertEqual(unresolved.iteration_unit, "environment_step")
        self.assertEqual(unresolved.iteration_unit_status, "explicit_user_approved")

    def test_seed_protocol_separates_train_eval_replay_model_exploration_seeds(self) -> None:
        protocol = self._seed_protocol()
        self.assertNotEqual(protocol.training_trace_generation_seed, protocol.evaluation_trace_generation_seed)
        self.assertNotEqual(protocol.replay_sampling_seed, protocol.model_initialization_seed)
        self.assertTrue(protocol.python_seeded_now)
        self.assertTrue(protocol.numpy_seeded_now)
        self.assertTrue(protocol.torch_seed_future_required)
        self.assertTrue(protocol.recorded_in_artifacts)

    def test_train_eval_split_uses_disjoint_trace_banks(self) -> None:
        protocol = self._split_protocol()
        self.assertTrue(protocol.fixed_evaluation_trace_bank)
        self.assertTrue(protocol.explicit_trace_ids)
        self.assertTrue(protocol.no_evaluation_on_training_traces)
        self.assertEqual(set(protocol.training_trace_ids) & set(protocol.evaluation_trace_ids), set())

    def test_checkpoint_schema_contains_reproducibility_metadata(self) -> None:
        checkpoint = self._checkpoint_schema()
        payload = checkpoint.to_dict()
        self.assertEqual(payload["feature_id"], "038-training-foundation-contract")
        self.assertIn("state_contract_version", payload)
        self.assertIn("action_contract_version", payload)
        self.assertIn("replay_schema_version", payload)
        self.assertIn("seed_bundle", payload)
        self.assertIn("training_step_counters", payload)
        self.assertIn("runtime_contract_refs", payload)
        self.assertTrue(payload["metadata_only"])
        self.assertTrue(payload["no_actual_model_checkpoint"])
        self.assertIsInstance(payload["commit_sha"], dict)
        self.assertIsInstance(payload["config_path"], dict)
        self.assertIsInstance(payload["config_hash"], dict)
        self.assertNotEqual(payload["commit_sha"], "2967c2a")
        self.assertNotEqual(payload["config_hash"], "deadbeef")

    def test_terminal_outcome_exposure_gate_blocks_training_when_terminal_ratio_insufficient(self) -> None:
        report = build_training_foundation_report(
            prerequisite_tags_verified=[{"tag": "037-baseline-revalidation-after-runtime-repair-complete", "commit": "69debe2f3c75e5cfe2e059c49e1063156c00130e"}],
            state_contract=self._state_contract(),
            action_index_contract=self._action_contract(),
            replay_schema=self._replay_schema(),
            target_update_frequency_contract=self._target_contract(),
            seed_protocol=self._seed_protocol(),
            train_eval_split_protocol=self._split_protocol(),
            checkpoint_schema=self._checkpoint_schema(),
            generated_arrivals=1000,
            decisions_exposed=980,
            finalized_terminal_tasks=10,
            completed_tasks=5,
            dropped_tasks=5,
            pending_at_horizon=970,
            per_policy_smoke_statistics=[{"policy": "random", "sample_size": 5}],
            runtime_contracts_verified=["Feature 032", "Feature 033"],
            threshold_approved=False,
        )
        gate = report.terminal_outcome_exposure_gate
        self.assertEqual(gate.threshold_status, "pending_user_approval")
        self.assertTrue(gate.training_blocked)
        self.assertEqual(gate.finalized_terminal_tasks, 10)
        self.assertEqual(gate.completed_tasks, 5)
        self.assertEqual(gate.dropped_tasks, 5)
        self.assertEqual(gate.pending_at_horizon, 970)
        self.assertGreater(gate.pending_transition_ratio, 0.0)


if __name__ == "__main__":
    unittest.main()
