from __future__ import annotations

from unittest import mock
import unittest

from src.analysis.completion_root_cause_diagnosis import CompletionRootCauseConfig, RootCauseClassifier, TaskLifecycleReconstructor, run_completion_root_cause_diagnosis
from src.analysis.completion_root_cause_diagnosis.runner import build_completion_root_cause_report


class CompletionRootCauseSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run_completion_root_cause_diagnosis()

    def test_config_defaults_match_paper_default_runtime(self) -> None:
        config = CompletionRootCauseConfig()
        self.assertEqual(config.feature_id, "045-completion-root-cause-diagnosis")
        self.assertEqual(config.episode_length, 110)
        self.assertEqual(config.timeout_slots, 20)
        self.assertEqual(config.node_count, 20)
        self.assertEqual(config.arrival_probability, 0.5)
        self.assertEqual(config.seeds, [0, 1, 2])
        self.assertEqual(config.strategies[0], "environment_default_policy_probe")
        self.assertTrue(config.no_runtime_repair)
        self.assertTrue(config.no_training)

    def test_report_schema_contains_required_fields(self) -> None:
        payload = self.report.to_dict()
        required = {
            "feature_id",
            "prerequisite_tags_verified",
            "prior_feature_gates_verified",
            "trace_input_sources",
            "paper_default_runtime_verified",
            "task_lifecycle_reconstruction_summary",
            "root_cause_evaluations",
            "dominant_root_causes",
            "per_action_root_cause_summary",
            "per_queue_root_cause_summary",
            "formula_consistency_summary",
            "deadline_ordering_summary",
            "reward_counter_path_summary",
            "diagnosis",
            "recommended_next_feature",
            "lifecycle_trace_sample",
            "trace_coverage_summary",
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
        }
        self.assertTrue(required.issubset(payload))
        self.assertEqual(payload["feature_id"], "045-completion-root-cause-diagnosis")
        self.assertTrue(payload["no_runtime_repair_performed"])
        self.assertTrue(payload["no_training_started"])

    def test_task_lifecycle_reconstruction_from_event_stream(self) -> None:
        events = [
            {
                "event_type": "task_generated",
                "slot": 0,
                "task_id": 7,
                "source_agent_id": 3,
                "selected_action": "local",
                "destination": "self",
                "queue_type": "pending_arrival",
                "host_node_id": None,
                "arrival_slot": 0,
                "absolute_deadline_slot": 20,
                "task_age_slots": 0,
                "size_mbits": 2.0,
                "processing_density_gcycles_per_mbit": 0.297,
                "cycles_required_gcycles": 0.594,
                "cycles_before_gcycles": None,
                "cycles_consumed_gcycles": None,
                "cycles_after_gcycles": None,
                "compute_capacity_gcycles_per_slot": None,
                "transmission_started_at": None,
                "transmission_completed_at": None,
                "transmission_delay_slots": None,
                "terminal_outcome": None,
                "reward": None,
                "reward_available": False,
                "pending_at_horizon": False,
                "legality_snapshot": {"local": True},
                "trace_source_component": "traffic_generator",
            },
            {
                "event_type": "task_admitted",
                "slot": 0,
                "task_id": 7,
                "source_agent_id": 3,
                "selected_action": "local",
                "destination": "self",
                "queue_type": "private",
                "host_node_id": "3",
                "arrival_slot": 0,
                "absolute_deadline_slot": 20,
                "task_age_slots": 0,
                "size_mbits": 2.0,
                "processing_density_gcycles_per_mbit": 0.297,
                "cycles_required_gcycles": 0.594,
                "cycles_before_gcycles": None,
                "cycles_consumed_gcycles": None,
                "cycles_after_gcycles": None,
                "compute_capacity_gcycles_per_slot": None,
                "transmission_started_at": None,
                "transmission_completed_at": None,
                "transmission_delay_slots": None,
                "terminal_outcome": None,
                "reward": None,
                "reward_available": False,
                "pending_at_horizon": False,
                "legality_snapshot": {"local": True},
                "trace_source_component": "environment",
            },
            {
                "event_type": "execution_started",
                "slot": 1,
                "task_id": 7,
                "source_agent_id": 3,
                "selected_action": "local",
                "destination": "self",
                "queue_type": "private",
                "host_node_id": "3",
                "arrival_slot": 0,
                "absolute_deadline_slot": 20,
                "task_age_slots": 1,
                "size_mbits": 2.0,
                "processing_density_gcycles_per_mbit": 0.297,
                "cycles_required_gcycles": 0.594,
                "cycles_before_gcycles": 0.594,
                "cycles_consumed_gcycles": 0.5,
                "cycles_after_gcycles": 0.094,
                "compute_capacity_gcycles_per_slot": 0.5,
                "transmission_started_at": None,
                "transmission_completed_at": None,
                "transmission_delay_slots": None,
                "terminal_outcome": None,
                "reward": None,
                "reward_available": False,
                "pending_at_horizon": False,
                "legality_snapshot": {"local": True},
                "trace_source_component": "environment",
            },
            {
                "event_type": "execution_progress",
                "slot": 1,
                "task_id": 7,
                "source_agent_id": 3,
                "selected_action": "local",
                "destination": "self",
                "queue_type": "private",
                "host_node_id": "3",
                "arrival_slot": 0,
                "absolute_deadline_slot": 20,
                "task_age_slots": 1,
                "size_mbits": 2.0,
                "processing_density_gcycles_per_mbit": 0.297,
                "cycles_required_gcycles": 0.594,
                "cycles_before_gcycles": 0.594,
                "cycles_consumed_gcycles": 0.5,
                "cycles_after_gcycles": 0.094,
                "compute_capacity_gcycles_per_slot": 0.5,
                "transmission_started_at": None,
                "transmission_completed_at": None,
                "transmission_delay_slots": None,
                "terminal_outcome": None,
                "reward": None,
                "reward_available": False,
                "pending_at_horizon": False,
                "legality_snapshot": {"local": True},
                "trace_source_component": "environment",
            },
            {
                "event_type": "task_completed",
                "slot": 2,
                "task_id": 7,
                "source_agent_id": 3,
                "selected_action": "local",
                "destination": "self",
                "queue_type": "private",
                "host_node_id": "3",
                "arrival_slot": 0,
                "absolute_deadline_slot": 20,
                "task_age_slots": 2,
                "size_mbits": 2.0,
                "processing_density_gcycles_per_mbit": 0.297,
                "cycles_required_gcycles": 0.594,
                "cycles_before_gcycles": 0.094,
                "cycles_consumed_gcycles": 0.094,
                "cycles_after_gcycles": 0.0,
                "compute_capacity_gcycles_per_slot": 0.5,
                "transmission_started_at": None,
                "transmission_completed_at": None,
                "transmission_delay_slots": None,
                "terminal_outcome": "completed",
                "reward": -2.0,
                "reward_available": True,
                "pending_at_horizon": False,
                "legality_snapshot": {"local": True},
                "trace_source_component": "environment",
            },
            {
                "event_type": "reward_emitted",
                "slot": 2,
                "task_id": 7,
                "source_agent_id": 3,
                "selected_action": "local",
                "destination": "self",
                "queue_type": "private",
                "host_node_id": "3",
                "arrival_slot": 0,
                "absolute_deadline_slot": 20,
                "task_age_slots": 2,
                "size_mbits": 2.0,
                "processing_density_gcycles_per_mbit": 0.297,
                "cycles_required_gcycles": 0.594,
                "cycles_before_gcycles": 0.094,
                "cycles_consumed_gcycles": 0.094,
                "cycles_after_gcycles": 0.0,
                "compute_capacity_gcycles_per_slot": 0.5,
                "transmission_started_at": None,
                "transmission_completed_at": None,
                "transmission_delay_slots": None,
                "terminal_outcome": "completed",
                "reward": -2.0,
                "reward_available": True,
                "pending_at_horizon": False,
                "legality_snapshot": {"local": True},
                "trace_source_component": "environment",
            },
        ]
        reconstructions = TaskLifecycleReconstructor.reconstruct("run-1", "environment_default_policy_probe", 0, events)
        self.assertEqual(len(reconstructions), 1)
        task = reconstructions[0]
        self.assertEqual(task.task_id, 7)
        self.assertEqual(task.arrival_slot, 0)
        self.assertEqual(task.absolute_deadline_slot, 20)
        self.assertEqual(task.generated_slot, 0)
        self.assertEqual(task.admitted_slot, 0)
        self.assertEqual(task.execution_started_at, 1)
        self.assertEqual(task.execution_completed_at, None)
        self.assertEqual(task.task_completed_at, 2)
        self.assertEqual(task.reward_emitted_at, 2)
        self.assertTrue(task.completed_before_deadline)
        self.assertTrue(task.reward_after_terminal_outcome)

    def test_trace_ingestion_rejects_non_paper_default_trace(self) -> None:
        with mock.patch(
            "src.analysis.completion_root_cause_diagnosis.runner._load_feature_044_report",
            return_value={
                "feature_id": "044-passive-runtime-lifecycle-trace-instrumentation",
                "lifecycle_trace_sample": [
                    {"size_mbits": 1.0, "processing_density_gcycles_per_mbit": 0.297, "arrival_slot": 0, "absolute_deadline_slot": 20}
                ],
                "paper_default_runtime_verified": {"episode_length": 111, "timeout_slots": 20},
            },
        ):
            with self.assertRaises(ValueError):
                build_completion_root_cause_report()


if __name__ == "__main__":
    unittest.main()
