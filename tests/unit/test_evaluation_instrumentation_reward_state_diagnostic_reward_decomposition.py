from __future__ import annotations

import unittest

from src.analysis.evaluation_instrumentation_reward_state_diagnostic.instrumented_evaluator import terminal_reward_from_task_dict
from src.analysis.evaluation_instrumentation_reward_state_diagnostic.runner import _build_reward_decomposition_result


class EvaluationInstrumentationRewardStateDiagnosticRewardDecompositionTests(unittest.TestCase):
    def test_terminal_reward_helper_matches_completed_and_dropped_outcomes(self) -> None:
        completed = terminal_reward_from_task_dict({"terminal_outcome": "completed", "arrival_slot": 10, "completion_slot": 13})
        dropped = terminal_reward_from_task_dict({"terminal_outcome": "dropped", "arrival_slot": 10, "completion_slot": 13})
        self.assertEqual(completed, -4.0)
        self.assertEqual(dropped, -40.0)

    def test_reward_decomposition_artifact_is_present(self) -> None:
        artifact = _build_reward_decomposition_result(
            [
                {
                    "training_budget": 100,
                    "reward_decomposition": {
                        "reward_by_action": {"local": 0.0, "horizontal": 0.0, "vertical": -6.0},
                        "reward_by_terminal_outcome": {"completed": -2.0, "dropped": -4.0},
                        "reward_by_action_and_terminal_outcome": {
                            "local": {"completed": {"count": 0, "total_reward": 0.0, "mean_reward": 0.0}, "dropped": {"count": 0, "total_reward": 0.0, "mean_reward": 0.0}},
                            "horizontal": {"completed": {"count": 0, "total_reward": 0.0, "mean_reward": 0.0}, "dropped": {"count": 0, "total_reward": 0.0, "mean_reward": 0.0}},
                            "vertical": {"completed": {"count": 1, "total_reward": -2.0, "mean_reward": -2.0}, "dropped": {"count": 2, "total_reward": -4.0, "mean_reward": -2.0}},
                        },
                        "drop_penalty_count_by_action": {"local": 0, "horizontal": 0, "vertical": 2},
                        "completion_reward_count_by_action": {"local": 0, "horizontal": 0, "vertical": 1},
                        "nan_reward_count": 0,
                        "zero_reward_count": 0,
                        "reward_available_count": 3,
                    },
                }
            ]
        )
        self.assertIn("100", artifact["by_checkpoint"])
        self.assertEqual(artifact["by_checkpoint"]["100"]["reward_available_count"], 3)


if __name__ == "__main__":
    unittest.main()
