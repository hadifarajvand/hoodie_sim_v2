from __future__ import annotations

import unittest
from unittest import mock

from src.analysis.evaluation_instrumentation_reward_state_diagnostic.runner import build_evaluation_instrumentation_reward_state_diagnostic_report

from tests.unit.test_evaluation_instrumentation_reward_state_diagnostic_action_logging import _FakeSession, _fake_policy_effect_result


class EvaluationInstrumentationRewardStateDiagnosticIntegrationTests(unittest.TestCase):
    def test_runner_uses_staged_budgets_and_no_5000_run(self) -> None:
        with mock.patch("src.analysis.evaluation_instrumentation_reward_state_diagnostic.runner.InstrumentedTrainingSession", side_effect=_FakeSession) as session_ctor, \
            mock.patch("src.analysis.evaluation_instrumentation_reward_state_diagnostic.runner.build_policy_effect_diagnostic", return_value=_fake_policy_effect_result()):
            report = build_evaluation_instrumentation_reward_state_diagnostic_report()

        payload = report.to_dict()
        self.assertEqual(payload["checkpoint_budgets"], [100, 150, 200, 500])
        self.assertEqual(payload["max_training_budget"], 500)
        self.assertFalse(payload["training_5000_run"])
        self.assertEqual(payload["training_mode"], "cumulative_staged_diagnostic")
        self.assertTrue(payload["evaluation_action_logging_repair_result"]["evaluation_action_distribution_present"])
        self.assertFalse(payload["replay_rolling_window_interpretation_repair_result"]["replay_window_is_full_training_history"])
        self.assertEqual(_FakeSession.last_instance.calls, [100, 150, 200, 500])


if __name__ == "__main__":
    unittest.main()
