from __future__ import annotations

import unittest

from src.analysis.controlled_evaluation_batch_readiness import report as batch_report
from src.analysis.controlled_evaluation_batch_readiness.report import build_controlled_evaluation_scenarios
from src.environment.paper_timeout import compute_absolute_deadline, is_success_before_deadline


class ControlledEvaluationBatchReadinessScenarioTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenarios = build_controlled_evaluation_scenarios()

    def test_required_scenario_ids_present(self) -> None:
        scenario_ids = {scenario.scenario_id for scenario in self.scenarios}
        self.assertEqual(
            scenario_ids,
            {
                "light_load_no_deadline_pressure",
                "tight_deadline_pressure",
                "legal_horizontal_offload",
                "illegal_horizontal_destination_attempt",
                "cloud_vertical_fallback",
                "timeout_drop_case",
                "mixed_local_horizontal_cloud_candidates",
            },
        )

    def test_local_success_before_deadline_does_not_use_horizontal_path(self) -> None:
        scenario = next(item for item in self.scenarios if item.scenario_id == "light_load_no_deadline_pressure")
        task = scenario.tasks[0]
        self.assertEqual(task.action_type, "local")
        self.assertEqual(task.destination_agent_id, "private")
        self.assertFalse(task.topology_check_required)
        self.assertTrue(task.topology_final_legal)
        self.assertEqual(task.topology_reason, "local_private_execution")
        self.assertTrue(scenario.passed)

    def test_horizontal_legal_neighbor_figure7(self) -> None:
        scenario = next(item for item in self.scenarios if item.scenario_id == "legal_horizontal_offload")
        task = scenario.tasks[0]
        self.assertEqual(task.action_type, "horizontal")
        self.assertEqual(task.destination_agent_id, "6")
        self.assertTrue(task.topology_check_required)
        self.assertTrue(task.topology_final_legal)
        self.assertTrue(batch_report._is_horizontal_neighbor("1", "6"))
        self.assertEqual(task.topology_neighbor_map_source, "specs/070-topology-timeout-reward-fidelity/evidence/figure-7-topology-extraction.md")

    def test_horizontal_non_neighbor_rejected(self) -> None:
        scenario = next(item for item in self.scenarios if item.scenario_id == "illegal_horizontal_destination_attempt")
        task = scenario.tasks[0]
        self.assertEqual(task.action_type, "horizontal")
        self.assertEqual(task.destination_agent_id, "2")
        self.assertTrue(task.topology_check_required)
        self.assertFalse(task.topology_final_legal)
        self.assertTrue(task.illegal_action_rejected)
        self.assertEqual(task.terminal_status, "dropped_unavailable")
        self.assertFalse(batch_report._is_horizontal_neighbor("1", "2"))

    def test_cloud_vertical_success_is_not_horizontal_adjacency(self) -> None:
        scenario = next(item for item in self.scenarios if item.scenario_id == "cloud_vertical_fallback")
        task = scenario.tasks[0]
        self.assertEqual(task.action_type, "cloud")
        self.assertEqual(task.destination_agent_id, "cloud")
        self.assertFalse(task.topology_check_required)
        self.assertTrue(task.topology_final_legal)
        self.assertEqual(task.topology_reason, "cloud_vertical_path")

    def test_default_batch_never_uses_compatibility_mode(self) -> None:
        self.assertTrue(all(not task.compatibility_mode_used for scenario in self.scenarios for task in scenario.tasks))
        self.assertTrue(all(task.mode == "paper" for scenario in self.scenarios for task in scenario.tasks))

    def test_compatibility_mode_is_not_the_default_deadline_behavior(self) -> None:
        arrival_slot = 2
        phi = 4
        deadline_slot = compute_absolute_deadline(arrival_slot, phi)
        self.assertTrue(is_success_before_deadline(deadline_slot, arrival_slot, phi))
        self.assertTrue(is_success_before_deadline(deadline_slot, arrival_slot, phi, mode="compatibility"))
        scenario = next(item for item in self.scenarios if item.scenario_id == "tight_deadline_pressure")
        self.assertEqual(scenario.tasks[0].completion_slot, deadline_slot)
        self.assertEqual(scenario.tasks[0].terminal_status, "completed_private")

    def test_horizontal_task_record_cannot_mark_non_neighbor_or_self_as_legal(self) -> None:
        non_neighbor = batch_report._horizontal_task_record(
            task_id="self-test-1",
            source_agent_id="1",
            destination_agent_id="2",
            arrival_slot=2,
            phi=4,
            completion_slot=4,
        )
        self.assertEqual(non_neighbor.terminal_status, "dropped_unavailable")
        self.assertFalse(non_neighbor.topology_final_legal)
        self.assertTrue(non_neighbor.illegal_action_rejected)

        self_neighbor = batch_report._horizontal_task_record(
            task_id="self-test-2",
            source_agent_id="1",
            destination_agent_id="1",
            arrival_slot=2,
            phi=4,
            completion_slot=4,
        )
        self.assertEqual(self_neighbor.terminal_status, "dropped_unavailable")
        self.assertFalse(self_neighbor.topology_final_legal)
        self.assertTrue(self_neighbor.illegal_action_rejected)
