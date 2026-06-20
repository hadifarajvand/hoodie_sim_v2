from __future__ import annotations

import unittest
from unittest import mock

from src.analysis.evaluation_instrumentation_reward_state_diagnostic.runner import build_evaluation_instrumentation_reward_state_diagnostic_report


def _fake_training_state(budget: int, *, index: int) -> dict[str, object]:
    return {
        "training_budget": budget,
        "cumulative_training_episode_count": budget,
        "optimizer_step_count": 100 + index,
        "replay_size": 10_000,
        "loss_count": 5 + index,
        "last_loss": 1.0 + index,
        "loss_finite": True,
        "reward_summary": {"reward_count": 100, "total_reward": -100.0, "mean_reward": -1.0, "pending_at_horizon_count": 0},
        "replay_window_action_distribution": {"local": 0, "horizontal": 0, "vertical": 10_000},
        "replay_window_is_full_training_history": False,
        "replay_window_capacity": 10_000,
        "replay_window_interpretation_warning": True,
        "cumulative_training_action_distribution": {"local": 10, "horizontal": 20, "vertical": 30},
        "training_action_sequence_sample": [{"episode_id": 0, "step_id": 0, "action": "vertical", "legal_action_mask": {"local": True}}],
    }


def _fake_evaluation_result(budget: int) -> dict[str, object]:
    action_distribution = {"local": 1, "horizontal": 2, "vertical": 3 if budget < 500 else 100}
    per_action = {
        "local": {"decision_count": 1, "completed_count": 0, "dropped_count": 0, "pending_at_horizon_count": 0, "terminal_transition_count": 0, "reward_bearing_transition_count": 0, "total_reward": 0.0, "mean_reward": 0.0, "completion_reward_count": 0, "drop_penalty_count": 0, "mean_completion_latency_slots": None, "mean_drop_latency_slots": None},
        "horizontal": {"decision_count": 2, "completed_count": 0, "dropped_count": 0, "pending_at_horizon_count": 0, "terminal_transition_count": 0, "reward_bearing_transition_count": 0, "total_reward": 0.0, "mean_reward": 0.0, "completion_reward_count": 0, "drop_penalty_count": 0, "mean_completion_latency_slots": None, "mean_drop_latency_slots": None},
        "vertical": {"decision_count": 3 if budget < 500 else 100, "completed_count": 1, "dropped_count": 2, "pending_at_horizon_count": 0, "terminal_transition_count": 3, "reward_bearing_transition_count": 3, "total_reward": -6.0, "mean_reward": -2.0, "completion_reward_count": 1, "drop_penalty_count": 2, "mean_completion_latency_slots": 3.0, "mean_drop_latency_slots": 4.0},
        "overall": {"decision_count": sum(action_distribution.values()), "completed_count": 1, "dropped_count": 2, "pending_at_horizon_count": 0, "terminal_transition_count": 3, "reward_bearing_transition_count": 3, "total_reward": -6.0, "mean_reward": -2.0, "mean_completion_latency_slots": 3.0, "mean_drop_latency_slots": 4.0},
    }
    return {
        "policy_name": f"candidate_policy_at_{budget}",
        "policy_kind": "candidate",
        "checkpoint_budget": budget,
        "evaluation_episode_count": 100,
        "episode_length": 110,
        "evaluation_trace_bank_id": "eval-bank",
        "same_evaluation_trace_bank": True,
        "evaluation_action_distribution_source": "evaluation_episodes",
        "evaluation_action_distribution": action_distribution,
        "evaluation_decision_count": sum(action_distribution.values()),
        "evaluation_action_sequence_sample": [{"episode_id": 0, "trace_id": "trace-0", "step_id": 0, "action": "vertical", "legal_action_mask": {"local": True}}],
        "evaluation_legal_action_mask_distribution": {"local=1|horizontal=1|vertical=1": 100},
        "evaluation_action_by_trace_id": {"trace-0": {"decision_count": 6, "action_distribution": action_distribution, "completed_count": 1, "dropped_count": 2, "pending_at_horizon_count": 0, "terminal_transition_count": 3, "reward_bearing_transition_count": 3, "episode_reward": -6.0, "policy_name": f"candidate_policy_at_{budget}", "policy_kind": "candidate"}},
        "evaluation_action_by_episode_id": {"0": {"decision_count": 6}},
        "completed_count": 1,
        "dropped_count": 2,
        "pending_at_horizon_count": 0,
        "mean_reward": -2.0,
        "evaluation_reward_summary": {
            "evaluation_episode_count": 100,
            "mean_reward": -2.0,
            "completed_task_count": 1,
            "dropped_task_count": 2,
            "terminal_transition_count": 3,
            "reward_bearing_transition_count": 3,
            "pending_at_horizon_count": 0,
            "trace_bank_disjoint": True,
            "trace_bank_ids": {"training": "train-bank", "evaluation": "eval-bank"},
            "trace_ids": ["trace-0"],
            "evaluation_on_training_traces": False,
            "same_evaluation_trace_bank": True,
        },
        "per_action_outcome_summary": per_action,
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
        "nan_reward_count": 0,
        "zero_reward_count": 0,
        "reward_available_count": 3,
        "candidate_policy_vertical_share": 1.0 if budget == 500 else 0.5,
    }


class _FakeSession:
    last_instance: "_FakeSession | None" = None

    def __init__(self, config) -> None:
        self.config = config
        self.campaign_config = type("Campaign", (), {"seed_bundle": type("SeedBundle", (), {"evaluation_trace_generation_seed": 100})(), "evaluation_trace_bank_id": "eval-bank"})()
        self.trainer = type("Trainer", (), {"config": type("TrainerConfig", (), {"training_trace_bank_id": "train-bank", "evaluation_trace_bank_id": "eval-bank"})()})()
        self.calls: list[int] = []
        _FakeSession.last_instance = self

    def train_to_budget(self, target_budget: int) -> dict[str, object]:
        self.calls.append(target_budget)
        return _fake_training_state(target_budget, index=len(self.calls))

    def candidate_policy_result(self, *, checkpoint_budget: int) -> dict[str, object]:
        return _fake_evaluation_result(checkpoint_budget)


def _fake_policy_effect_result() -> dict[str, object]:
    policy_results = {f"candidate_policy_at_{budget}": _fake_evaluation_result(budget) for budget in [100, 150, 200, 500]}
    policy_results.update(
        {
            "fixed_local_policy": _fake_evaluation_result(100),
            "fixed_horizontal_policy": _fake_evaluation_result(100),
            "fixed_vertical_policy": _fake_evaluation_result(100),
            "random_legal_policy": _fake_evaluation_result(100),
        }
    )
    return {
        "evaluation_trace_bank_id": "eval-bank",
        "evaluation_episode_count": 100,
        "episode_length": 110,
        "candidate_policy_vertical_collapse_in_evaluation": True,
        "candidate_policy_vertical_collapse_in_training_replay_window": True,
        "policy_affects_reward": "false",
        "policy_affects_terminal_outcomes": "false",
        "evaluation_metric_static_because_policy_same": "false",
        "evaluation_metric_static_because_reward_aggregation": "true",
        "evaluation_metric_static_because_environment_dynamics": "uncertain",
        "evaluation_reward_static_after_instrumentation": True,
        "policy_results": policy_results,
        "candidate_reward_variation": 0.0,
        "candidate_action_distribution_changed_by_budget": True,
        "candidate_terminal_outcomes_changed_by_budget": False,
    }


class EvaluationInstrumentationRewardStateDiagnosticActionLoggingTests(unittest.TestCase):
    def test_action_logging_and_replay_warning_are_reported(self) -> None:
        with mock.patch("src.analysis.evaluation_instrumentation_reward_state_diagnostic.runner.InstrumentedTrainingSession", side_effect=_FakeSession) as session_ctor, \
            mock.patch("src.analysis.evaluation_instrumentation_reward_state_diagnostic.runner.build_policy_effect_diagnostic", return_value=_fake_policy_effect_result()):
            report = build_evaluation_instrumentation_reward_state_diagnostic_report()

        payload = report.to_dict()
        self.assertEqual(payload["checkpoint_budgets"], [100, 150, 200, 500])
        self.assertEqual(payload["max_training_budget"], 500)
        self.assertEqual(payload["training_mode"], "cumulative_staged_diagnostic")
        self.assertFalse(payload["training_5000_run"])
        self.assertEqual(session_ctor.call_count, 1)
        self.assertEqual(_FakeSession.last_instance.calls, [100, 150, 200, 500])
        self.assertEqual(payload["evaluation_action_logging_repair_result"]["evaluation_action_distribution_source"], "evaluation_episodes")
        self.assertTrue(payload["evaluation_action_logging_repair_result"]["evaluation_action_distribution_present"])
        self.assertFalse(payload["replay_rolling_window_interpretation_repair_result"]["replay_window_is_full_training_history"])
        self.assertTrue(payload["replay_rolling_window_interpretation_repair_result"]["replay_window_interpretation_warning"])
        self.assertTrue(all("evaluation_action_distribution" in checkpoint for checkpoint in payload["checkpoint_metrics"]))
        self.assertTrue(all("per_action_outcome_summary" in checkpoint for checkpoint in payload["checkpoint_metrics"]))
        self.assertTrue(all("reward_decomposition" in checkpoint for checkpoint in payload["checkpoint_metrics"]))


if __name__ == "__main__":
    unittest.main()
