from __future__ import annotations

import unittest

from src.analysis.hoodie_runtime_evaluation_runner.config import EvaluationConfig, REQUIRED_SCENARIOS, WORKLOAD_LEVELS
from src.analysis.hoodie_runtime_evaluation_runner.report import build_execution_rows
from src.analysis.hoodie_runtime_evaluation_runner.scenarios import build_scenario_contexts


class HoodieRuntimeEvaluationRunnerScenarioTests(unittest.TestCase):
    def test_scenario_expansion_matches_expected_context_count(self) -> None:
        config = EvaluationConfig()
        contexts = build_scenario_contexts(config)
        self.assertEqual(len(contexts), 3 * 3 * 3 * len(REQUIRED_SCENARIOS))
        self.assertEqual({context.topology_mode for context in contexts}, {"paper_figure_7"})
        self.assertEqual({context.runtime_mode for context in contexts}, {"paper"})
        self.assertEqual({context.workload for context in contexts}, set(WORKLOAD_LEVELS))

    def test_execution_rows_cover_all_policies_and_scenarios(self) -> None:
        rows, scenarios, outcomes_by_key = build_execution_rows(EvaluationConfig())
        self.assertEqual(len(rows), 1323)
        self.assertEqual(len(scenarios), 189)
        self.assertEqual(len(outcomes_by_key), 1323)
        self.assertTrue(all(len(outcomes) > 0 for outcomes in outcomes_by_key.values()))


if __name__ == "__main__":
    unittest.main()
