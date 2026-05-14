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
    TrainEvalSplitProtocol,
    build_training_foundation_report,
    write_training_foundation_report,
)


class TrainingFoundationContractReportIntegrationTests(unittest.TestCase):
    def _report(self):
        return build_training_foundation_report(
            prerequisite_tags_verified=[{"tag": "037-baseline-revalidation-after-runtime-repair-complete", "commit": "69debe2f3c75e5cfe2e059c49e1063156c00130e"}],
            state_contract=StateContract(
                version="1.0",
                agent_key_field="edge_agent_id",
                field_order=["queue_length", "queue_delay", "available_capacity"],
                field_types={"queue_length": "int", "queue_delay": "float", "available_capacity": "float"},
                normalization_rules={"queue_delay": "divide_by_slot_duration"},
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
            ),
            target_update_frequency_contract=TargetUpdateFrequencyContract(
                update_frequency=2000,
                iteration_unit=None,
                iteration_unit_status="unresolved_pending_user_approval",
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
                training_trace_ids=["train-a", "train-b"],
                evaluation_trace_ids=["eval-a"],
                fixed_evaluation_trace_bank=True,
                explicit_trace_ids=True,
                no_evaluation_on_training_traces=True,
                no_unfair_baseline_hoodie_trace_mismatch=True,
            ),
            checkpoint_schema=CheckpointSchema(
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
            ),
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

    def test_training_foundation_report_schema(self) -> None:
        report = self._report()
        payload = report.to_dict()
        required_keys = {
            "feature_id",
            "prerequisite_tags_verified",
            "state_contract",
            "action_index_contract",
            "replay_schema",
            "target_update_frequency_contract",
            "seed_protocol",
            "train_eval_split_protocol",
            "checkpoint_schema",
            "terminal_outcome_exposure_gate",
            "runtime_contracts_verified",
            "no_training_started",
            "no_neural_network_change",
            "no_dependency_drift",
            "no_environment_contract_drift",
            "no_reward_timing_change",
            "no_policy_drift",
            "no_curve_fitting",
            "no_paper_reproduction_claim",
            "final_verdict",
        }
        self.assertTrue(required_keys.issubset(payload))
        self.assertEqual(payload["feature_id"], "038-training-foundation-contract")
        self.assertTrue(payload["no_training_started"])
        self.assertTrue(payload["no_dependency_drift"])
        self.assertTrue(payload["no_environment_contract_drift"])
        self.assertTrue(payload["no_reward_timing_change"])
        self.assertTrue(payload["no_policy_drift"])
        self.assertTrue(payload["no_curve_fitting"])
        self.assertTrue(payload["no_paper_reproduction_claim"])
        self.assertEqual(payload["terminal_outcome_exposure_gate"]["threshold_status"], "pending_user_approval")
        self.assertTrue(payload["terminal_outcome_exposure_gate"]["training_blocked"])
        self.assertEqual(payload["replay_schema"]["pending_at_horizon_policy"], "explicit_pending_at_horizon")
        self.assertEqual(payload["target_update_frequency_contract"]["update_frequency"], 2000)
        self.assertIsNone(payload["target_update_frequency_contract"]["iteration_unit"])
        self.assertEqual(payload["target_update_frequency_contract"]["iteration_unit_status"], "unresolved_pending_user_approval")
        self.assertNotEqual(payload["checkpoint_schema"]["commit_sha"], "2967c2a")
        self.assertNotEqual(payload["checkpoint_schema"]["config_hash"], "deadbeef")
        self.assertTrue(payload["checkpoint_schema"]["metadata_only"])
        self.assertTrue(payload["checkpoint_schema"]["no_actual_model_checkpoint"])

    def test_training_foundation_artifacts_are_written(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report = self._report()
            json_path, md_path = write_training_foundation_report(report, Path(tmpdir) / "artifacts")
            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["feature_id"], "038-training-foundation-contract")
            self.assertIn("terminal_outcome_exposure_gate", payload)
            self.assertIn("pending_user_approval", md_path.read_text(encoding="utf-8"))
            self.assertIn("no_training_started", md_path.read_text(encoding="utf-8"))
            self.assertIsNone(payload["target_update_frequency_contract"]["iteration_unit"])
            self.assertEqual(payload["target_update_frequency_contract"]["iteration_unit_status"], "unresolved_pending_user_approval")
            self.assertIsInstance(payload["checkpoint_schema"]["commit_sha"], dict)
            self.assertIsInstance(payload["checkpoint_schema"]["config_hash"], dict)


if __name__ == "__main__":
    unittest.main()
