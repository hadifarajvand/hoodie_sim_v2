from __future__ import annotations

import unittest
from unittest import mock

from src.analysis.evaluation_instrumentation_reward_state_diagnostic.runner import build_evaluation_instrumentation_reward_state_diagnostic_report

from tests.unit.test_evaluation_instrumentation_reward_state_diagnostic_action_logging import _FakeSession, _fake_policy_effect_result


class EvaluationInstrumentationRewardStateDiagnosticScopeGuardTests(unittest.TestCase):
    def test_forbidden_paths_block_release_ready_report(self) -> None:
        _FakeSession.last_instance = None
        with mock.patch("src.analysis.evaluation_instrumentation_reward_state_diagnostic.runner.git_status_paths", return_value=["src/environment/reward_timing.py"]), \
            mock.patch("src.analysis.evaluation_instrumentation_reward_state_diagnostic.runner.git_staged_paths", return_value=[]), \
            mock.patch("src.analysis.evaluation_instrumentation_reward_state_diagnostic.runner.git_diff_paths", return_value=[]), \
            mock.patch("src.analysis.evaluation_instrumentation_reward_state_diagnostic.runner.InstrumentedTrainingSession", side_effect=_FakeSession) as session_ctor, \
            mock.patch("src.analysis.evaluation_instrumentation_reward_state_diagnostic.runner.build_policy_effect_diagnostic", return_value=_fake_policy_effect_result()):
            report = build_evaluation_instrumentation_reward_state_diagnostic_report()

        payload = report.to_dict()
        self.assertEqual(payload["final_verdict"], "evaluation_instrumentation_diagnostic_blocked")
        self.assertIn("scope_drift_detected", payload["remaining_blockers"])
        self.assertEqual(session_ctor.call_count, 0)
        self.assertIsNone(_FakeSession.last_instance)


if __name__ == "__main__":
    unittest.main()
