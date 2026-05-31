from __future__ import annotations

import math
import unittest

from src.analysis.end_to_end_hoodie_golden_trace_validation.model import GoldenTraceScenario, GoldenTraceStep


class EndToEndHoodieGoldenTraceValidationModelTests(unittest.TestCase):
    def _required_steps(self) -> tuple[GoldenTraceStep, ...]:
        return tuple(
            GoldenTraceStep(
                step_name=step_name,
                input_snapshot={"step": step_name},
                expected_output={"value": step_name},
                actual_output={"value": step_name},
                passed=True,
                evidence_source="tests.unit.test_end_to_end_hoodie_golden_trace_validation_model",
            )
            for step_name in (
                "task_arrival",
                "action_selection",
                "topology_legality",
                "deadline_computation",
                "terminal_state_assignment",
                "reward_emission",
                "expected_actual_comparison",
            )
        )

    def test_golden_trace_step_compares_expected_and_actual_outputs(self) -> None:
        step = GoldenTraceStep(
            step_name="task_arrival",
            input_snapshot={"arrival_slot": 2},
            expected_output={"reward_value": float("nan")},
            actual_output={"reward_value": float("nan")},
            passed=True,
            evidence_source="src.environment.reward_timing.reward_from_terminal_state",
        )
        self.assertTrue(step.passed)
        self.assertTrue(math.isnan(step.actual_output["reward_value"]))
        payload = step.to_dict()
        self.assertEqual(payload["step_name"], "task_arrival")

        with self.assertRaises(ValueError):
            GoldenTraceStep(
                step_name="reward_emission",
                input_snapshot={"terminal_status": "completed_private"},
                expected_output={"reward_value": -3.0},
                actual_output={"reward_value": -4.0},
                passed=True,
                evidence_source="src.environment.reward_timing.reward_for_terminal_task",
            )

    def test_golden_trace_scenario_requires_non_empty_steps(self) -> None:
        with self.assertRaises(ValueError):
            GoldenTraceScenario(
                scenario_id="empty",
                name="Empty",
                description="empty",
                inputs={},
                expected_outputs={},
                actual_outputs={},
                steps=(),
            )

    def test_golden_trace_scenario_requires_required_steps(self) -> None:
        scenario = GoldenTraceScenario(
            scenario_id="partial",
            name="Partial",
            description="missing steps fail",
            inputs={"arrival_slot": 2},
            expected_outputs={"status": "ok"},
            actual_outputs={"status": "ok"},
            steps=(self._required_steps()[0],),
        )
        self.assertFalse(scenario.passed)

    def test_golden_trace_scenario_rejects_shared_expected_and_actual_identity(self) -> None:
        payload = {"status": "ok"}
        with self.assertRaises(ValueError):
            GoldenTraceScenario(
                scenario_id="shared",
                name="Shared",
                description="shared references must fail",
                inputs={"status": "ok"},
                expected_outputs=payload,
                actual_outputs=payload,
                steps=self._required_steps(),
            )

    def test_golden_trace_scenario_fails_when_deadline_expected_and_actual_diverge(self) -> None:
        steps = self._required_steps()
        scenario = GoldenTraceScenario(
            scenario_id="deadline-mismatch",
            name="Deadline Mismatch",
            description="expected deadline divergence must fail",
            inputs={"arrival_slot": 2},
            expected_outputs={"deadline": {"absolute_deadline_slot": 5}},
            actual_outputs={"deadline": {"absolute_deadline_slot": 4}},
            steps=steps,
        )
        self.assertFalse(scenario.passed)

    def test_golden_trace_scenario_fails_when_reward_expected_and_actual_diverge(self) -> None:
        steps = self._required_steps()
        scenario = GoldenTraceScenario(
            scenario_id="reward-mismatch",
            name="Reward Mismatch",
            description="expected reward divergence must fail",
            inputs={"arrival_slot": 2},
            expected_outputs={"reward": {"reward_value": -3.0}},
            actual_outputs={"reward": {"reward_value": -4.0}},
            steps=steps,
        )
        self.assertFalse(scenario.passed)

    def test_golden_trace_scenario_passes_with_required_steps(self) -> None:
        from src.analysis.end_to_end_hoodie_golden_trace_validation.report import build_all_golden_trace_scenarios

        scenarios = build_all_golden_trace_scenarios()
        self.assertEqual(len(scenarios), 11)
        self.assertTrue(all(scenario.passed for scenario in scenarios))


if __name__ == "__main__":
    unittest.main()
