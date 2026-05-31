from __future__ import annotations

import math
import unittest

from src.analysis.end_to_end_hoodie_golden_trace_validation.model import GoldenTraceScenario, GoldenTraceStep


class EndToEndHoodieGoldenTraceValidationModelTests(unittest.TestCase):
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
        step = GoldenTraceStep(
            step_name="task_arrival",
            input_snapshot={"arrival_slot": 2},
            expected_output={"arrival_slot": 2},
            actual_output={"arrival_slot": 2},
            passed=True,
            evidence_source="src.analysis.end_to_end_hoodie_golden_trace_validation.report",
        )
        scenario = GoldenTraceScenario(
            scenario_id="partial",
            name="Partial",
            description="missing steps fail",
            inputs={"arrival_slot": 2},
            expected_outputs={"status": "ok"},
            actual_outputs={"status": "ok"},
            steps=(step,),
        )
        self.assertFalse(scenario.passed)

    def test_golden_trace_scenario_passes_with_required_steps(self) -> None:
        from src.analysis.end_to_end_hoodie_golden_trace_validation.report import build_all_golden_trace_scenarios

        scenarios = build_all_golden_trace_scenarios()
        self.assertEqual(len(scenarios), 11)
        self.assertTrue(all(scenario.passed for scenario in scenarios))


if __name__ == "__main__":
    unittest.main()
