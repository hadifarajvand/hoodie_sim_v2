from __future__ import annotations

import unittest

from src.analysis.hoodie_evaluation_runner.config import EvaluationConfig
from src.analysis.hoodie_evaluation_runner.scenarios import build_scenario_contexts


class HoodieEvaluationRunnerScenarioTests(unittest.TestCase):
    def test_deterministic_scenario_expansion_covers_required_shape(self) -> None:
        config = EvaluationConfig(
            policies=("HOODIE_PROPOSED",),
            scenarios=("light_load_no_deadline_pressure", "tight_deadline_pressure"),
            workloads=("low", "high"),
            deadline_pressures=("relaxed", "tight"),
            seeds=(7, 13),
        )
        scenarios = build_scenario_contexts(config)
        self.assertEqual(len(scenarios), 16)
        self.assertEqual({scenario.scenario_name for scenario in scenarios}, {"light_load_no_deadline_pressure", "tight_deadline_pressure"})
        self.assertEqual({scenario.workload for scenario in scenarios}, {"low", "high"})
        self.assertEqual({scenario.deadline_pressure for scenario in scenarios}, {"relaxed", "tight"})
        self.assertTrue(all(scenario.tasks for scenario in scenarios))
        self.assertTrue(all(len(scenario.deadline_slots) == scenario.task_count for scenario in scenarios))
        self.assertTrue(all(scenario.topology_mode == "paper_figure_7" for scenario in scenarios))
        self.assertTrue(all(scenario.runtime_mode == "paper" for scenario in scenarios))


if __name__ == "__main__":
    unittest.main()
