from __future__ import annotations

import math
import unittest

from src.analysis.end_to_end_hoodie_golden_trace_validation.report import build_all_golden_trace_scenarios


class EndToEndHoodieGoldenTraceValidationScenarioTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenarios = {scenario.scenario_id: scenario for scenario in build_all_golden_trace_scenarios()}

    def test_local_success_before_deadline(self) -> None:
        scenario = self.scenarios["local_success_before_deadline"]
        self.assertTrue(scenario.passed)
        self.assertEqual(scenario.inputs["action_type"], "local")
        self.assertFalse(scenario.actual_outputs["topology"]["topology_check_required"])
        self.assertEqual(scenario.actual_outputs["topology"]["reason"], "local_private_execution")
        self.assertEqual(scenario.actual_outputs["action_selection"]["selected_destination"], "private")
        self.assertIsNot(scenario.expected_outputs, scenario.actual_outputs)
        self.assertEqual(scenario.expected_outputs["deadline"]["terminal_status"], "completed_private")
        self.assertEqual(scenario.actual_outputs["reward"]["reward_value"], -3.0)

    def test_local_timeout_at_deadline(self) -> None:
        scenario = self.scenarios["local_timeout_at_deadline"]
        self.assertTrue(scenario.passed)
        self.assertEqual(scenario.actual_outputs["deadline"]["terminal_status"], "completed_private")
        self.assertEqual(scenario.actual_outputs["reward"]["reward_value"], -4.0)
        self.assertTrue(scenario.actual_outputs["deadline"]["success_before_deadline"])

    def test_horizontal_legal_neighbor_figure7(self) -> None:
        scenario = self.scenarios["horizontal_legal_neighbor_figure7"]
        self.assertTrue(scenario.passed)
        self.assertTrue(scenario.actual_outputs["topology"]["final_legal"])
        self.assertEqual(scenario.actual_outputs["topology"]["destination_agent_id"], "6")
        self.assertTrue(scenario.actual_outputs["topology"]["topology_check_required"])

    def test_horizontal_non_neighbor_rejected(self) -> None:
        scenario = self.scenarios["horizontal_non_neighbor_rejected"]
        self.assertTrue(scenario.passed)
        self.assertFalse(scenario.actual_outputs["topology"]["final_legal"])
        self.assertEqual(scenario.actual_outputs["terminal_state"]["terminal_status"], "dropped_unavailable")
        self.assertEqual(scenario.actual_outputs["topology"]["destination_agent_id"], "2")

    def test_horizontal_self_destination_rejected(self) -> None:
        scenario = self.scenarios["horizontal_self_destination_rejected"]
        self.assertTrue(scenario.passed)
        self.assertTrue(scenario.actual_outputs["topology"]["is_self_destination"])
        self.assertFalse(scenario.actual_outputs["topology"]["final_legal"])
        self.assertEqual(scenario.actual_outputs["topology"]["destination_agent_id"], "1")

    def test_cloud_vertical_success(self) -> None:
        scenario = self.scenarios["cloud_vertical_success"]
        self.assertTrue(scenario.passed)
        self.assertEqual(scenario.actual_outputs["topology"]["destination_agent_id"], "cloud")
        self.assertTrue(scenario.actual_outputs["topology"]["final_legal"])
        self.assertEqual(scenario.actual_outputs["terminal_state"]["terminal_status"], "completed_cloud")

    def test_success_reward_negative_phi(self) -> None:
        scenario = self.scenarios["success_reward_negative_phi"]
        self.assertTrue(scenario.passed)
        self.assertEqual(scenario.actual_outputs["action_selection"]["action_type"], "local")
        self.assertEqual(scenario.actual_outputs["reward"]["reward_value"], -4.0)

    def test_drop_reward_negative_c(self) -> None:
        scenario = self.scenarios["drop_reward_negative_c"]
        self.assertTrue(scenario.passed)
        self.assertEqual(scenario.actual_outputs["reward"]["reward_value"], -40.0)
        self.assertFalse(scenario.actual_outputs["deadline"]["success_before_deadline"])

    def test_inactive_task_no_reward_sentinel(self) -> None:
        scenario = self.scenarios["inactive_task_no_reward_sentinel"]
        self.assertTrue(scenario.passed)
        self.assertTrue(math.isnan(scenario.actual_outputs["reward"]["reward_value"]))
        self.assertEqual(scenario.actual_outputs["action_selection"]["action_type"], "local")

    def test_pending_task_cannot_emit_reward(self) -> None:
        scenario = self.scenarios["pending_task_cannot_emit_reward"]
        self.assertTrue(scenario.passed)
        self.assertEqual(scenario.actual_outputs["reward"]["status"], "blocked")
        self.assertFalse(scenario.actual_outputs["reward"]["can_emit_reward"])
        self.assertIsNone(scenario.actual_outputs["reward"]["reward_trace"]["reward_value"])
        self.assertEqual(scenario.actual_outputs["terminal_state"]["terminal_status"], "pending")

    def test_compatibility_mode_not_default(self) -> None:
        scenario = self.scenarios["compatibility_mode_not_default"]
        self.assertTrue(scenario.passed)
        self.assertTrue(scenario.actual_outputs["deadline"]["paper"]["success_before_deadline"])
        self.assertTrue(scenario.actual_outputs["deadline"]["compatibility"]["success_before_deadline"])
        self.assertEqual(scenario.actual_outputs["reward"]["paper"]["reward_value"], -3.0)
        self.assertEqual(scenario.actual_outputs["reward"]["compatibility"]["reward_value"], -2.0)
        self.assertEqual(scenario.actual_outputs["action_selection"]["action_type"], "local")


if __name__ == "__main__":
    unittest.main()
