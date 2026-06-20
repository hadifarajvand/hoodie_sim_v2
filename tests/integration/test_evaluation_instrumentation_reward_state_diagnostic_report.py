from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src.analysis.evaluation_instrumentation_reward_state_diagnostic.config import (
    DIAGNOSTIC_DECISION_JSON,
    EVALUATION_ACTION_DISTRIBUTION_JSON,
    FIGURE_MANIFEST_JSON,
    FINAL_DIAGNOSTIC_SUMMARY_MD,
    INSTRUMENTED_CHECKPOINT_METRICS_JSON,
    PER_ACTION_OUTCOME_SUMMARY_JSON,
    POLICY_EFFECT_DIAGNOSTIC_JSON,
    REPLAY_WINDOW_VS_CUMULATIVE_TRAINING_ACTIONS_JSON,
    REPORT_JSON,
    REPORT_MD,
    REWARD_DECOMPOSITION_JSON,
    STATE_FEATURE_COVERAGE_AUDIT_JSON,
)
from src.analysis.evaluation_instrumentation_reward_state_diagnostic.runner import generate_evaluation_instrumentation_reward_state_diagnostic_artifacts, run_evaluation_instrumentation_reward_state_diagnostic

from tests.unit.test_evaluation_instrumentation_reward_state_diagnostic_action_logging import _FakeSession, _fake_policy_effect_result


class EvaluationInstrumentationRewardStateDiagnosticReportIntegrationTests(unittest.TestCase):
    def test_required_artifacts_exist_after_generation(self) -> None:
        with mock.patch("src.analysis.evaluation_instrumentation_reward_state_diagnostic.runner.InstrumentedTrainingSession", side_effect=_FakeSession), \
            mock.patch("src.analysis.evaluation_instrumentation_reward_state_diagnostic.runner.build_policy_effect_diagnostic", return_value=_fake_policy_effect_result()):
            with tempfile.TemporaryDirectory() as tmp_dir:
                report = run_evaluation_instrumentation_reward_state_diagnostic(output_dir=Path(tmp_dir))
                payload = report.to_dict()
                self.assertEqual(payload["final_verdict"], "evaluation_instrumentation_diagnostic_ready")
                paths = [
                    Path(tmp_dir) / REPORT_JSON.name,
                    Path(tmp_dir) / REPORT_MD.name,
                    Path(tmp_dir) / INSTRUMENTED_CHECKPOINT_METRICS_JSON.name,
                    Path(tmp_dir) / EVALUATION_ACTION_DISTRIBUTION_JSON.name,
                    Path(tmp_dir) / PER_ACTION_OUTCOME_SUMMARY_JSON.name,
                    Path(tmp_dir) / REWARD_DECOMPOSITION_JSON.name,
                    Path(tmp_dir) / REPLAY_WINDOW_VS_CUMULATIVE_TRAINING_ACTIONS_JSON.name,
                    Path(tmp_dir) / STATE_FEATURE_COVERAGE_AUDIT_JSON.name,
                    Path(tmp_dir) / POLICY_EFFECT_DIAGNOSTIC_JSON.name,
                    Path(tmp_dir) / DIAGNOSTIC_DECISION_JSON.name,
                    Path(tmp_dir) / FINAL_DIAGNOSTIC_SUMMARY_MD.name,
                    Path(tmp_dir) / FIGURE_MANIFEST_JSON.name,
                ]
                self.assertTrue(all(path.exists() for path in paths))
                self.assertTrue(all((Path(tmp_dir) / "figures" / name).exists() for name in [
                    "figure_01_evaluation_action_distribution_by_budget.png",
                    "figure_02_canonical_per_action_drop_completion_by_budget.png",
                    "figure_03_raw_vs_canonical_reward_by_budget.png",
                    "figure_04_replay_window_vs_cumulative_training_actions.png",
                    "figure_05_policy_effect_canonical_reward.png",
                    "figure_06_state_feature_coverage_matrix.png",
                    "figure_07_canonical_drop_completion_ratio_by_budget.png",
                ]))


if __name__ == "__main__":
    unittest.main()
