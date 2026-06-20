from __future__ import annotations

import unittest
from unittest import mock
from pathlib import Path

from src.analysis.reward_emission_evaluation_metric_aggregation_repair.reconciliation import build_canonical_task_reconciliation
from src.analysis.reward_emission_evaluation_metric_aggregation_repair.runner import run_reward_emission_aggregation_repair, write_artifacts

from tests.unit.test_reward_emission_evaluation_metric_aggregation_repair_reconciliation import _task_records


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


def _fake_evaluation_result(*args, **kwargs) -> dict[str, object]:
    budget = int(kwargs.get("checkpoint_budget") or (args[0] if args else 100))
    task_records = _task_records()
    reconciliation = build_canonical_task_reconciliation(
        checkpoint_budget=budget,
        evaluation_decision_count=3,
        task_records=task_records,
    )
    action_distribution = {"local": 1, "horizontal": 1, "vertical": 1}
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
        "evaluation_decision_count": 3,
        "evaluation_action_sequence_sample": [{"episode_id": 0, "trace_id": "trace-0", "task_id": 1, "selected_action": "vertical"}],
        "evaluation_legal_action_mask_distribution": {"local=1|horizontal=1|vertical=1": 3},
        "evaluation_action_by_trace_id": {"trace-0": {"decision_count": 3}},
        "evaluation_action_by_episode_id": {"0": {"decision_count": 3}},
        "decision_records_summary": {"decision_count": 3, "sample_records": [{"trace_id": "trace-0", "episode_id": 0, "task_id": 1, "selected_action": "vertical"}], "evaluation_action_distribution_source": "evaluation_episodes"},
        "terminal_event_records": {"record_count": 3, "sample_records": [{"trace_id": "trace-0", "episode_id": 0, "task_id": 1}], "recovered_from_finalized_tasks": True},
        "reward_event_records": {"record_count": 2, "sample_records": [{"trace_id": "trace-0", "episode_id": 0, "task_id": 1, "raw_reward": -40.0}], "reward_available_count": 2, "raw_reward_event_recovery_blocked": False},
        "task_records": task_records,
        "episode_summaries": [{"episode_id": 0, "trace_id": "trace-0", "decision_count": 3, "terminal_task_count": 2, "completion_count": 1, "drop_count": 1, "pending_count": 1, "unknown_count": 0, "raw_reward_event_count": 2, "raw_reward_total": -44.0, "canonical_reward_total": -44.0, "reward_recovered": True}],
        "reward_reconciliation_tolerance": 1e-9,
        "raw_reward_event_recovery_blocked": False,
        "terminal_event_recovery_blocked": False,
        "raw_reward_event_count": 2,
        "raw_reward_total": -44.0,
        "raw_terminal_event_count": 3,
        "raw_lifecycle_terminal_event_count": 3,
        "episode_reward_totals": [-44.0],
        "candidate_policy_vertical_share": 1.0 / 3.0,
        "evaluation_reward_summary": {
            "evaluation_episode_count": 100,
            "mean_reward": -44.0,
            "completed_task_count": 1,
            "dropped_task_count": 1,
            "pending_at_horizon_count": 1,
            "unknown_task_count": 0,
            "terminal_transition_count": 2,
            "reward_bearing_transition_count": 2,
            "canonical_task_count": 3,
            "canonical_task_reward_total": -44.0,
            "canonical_task_reward_count": 2,
            "raw_terminal_event_count": 3,
            "raw_reward_emission_count": 2,
            "raw_event_reward_total": -44.0,
            "raw_event_reward_count": 2,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_available_count": 2,
            "raw_reward_event_recovery_blocked": False,
            "terminal_event_recovery_blocked": False,
            "trace_bank_disjoint": True,
            "trace_bank_ids": {"training": "train-bank", "evaluation": "eval-bank"},
            "trace_ids": ["trace-0"],
            "evaluation_on_training_traces": False,
            "same_evaluation_trace_bank": True,
            "candidate_reproduction_supported": True,
        },
        "reward_reconciled": reconciliation["raw_vs_canonical_reward_reconciliation"]["reward_reconciled"],
        "raw_vs_canonical_reward_reconciliation": reconciliation["raw_vs_canonical_reward_reconciliation"],
        "canonical_task_outcome_summary": reconciliation["canonical_task_outcome_summary"],
        "canonical_reward_decomposition": reconciliation["canonical_reward_decomposition"],
        "paper_aligned_diagnostic_metrics": reconciliation["paper_aligned_diagnostic_metrics"],
        "per_action_outcome_summary": reconciliation["canonical_task_outcome_summary"]["by_action"],
        "completed_count": reconciliation["canonical_task_outcome_summary"]["overall"]["canonical_completion_count"],
        "dropped_count": reconciliation["canonical_task_outcome_summary"]["overall"]["canonical_drop_count"],
        "pending_at_horizon_count": reconciliation["canonical_task_outcome_summary"]["overall"]["canonical_pending_count"],
        "unknown_count": reconciliation["canonical_task_outcome_summary"]["overall"]["canonical_unknown_count"],
        "raw_event_reward_total": reconciliation["raw_vs_canonical_reward_reconciliation"]["raw_event_reward_total"],
        "canonical_task_reward_total": reconciliation["raw_vs_canonical_reward_reconciliation"]["canonical_task_reward_total"],
        "reward_reconciliation_status": "passed",
    }


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
        "raw_event_reward_static_across_budget": False,
        "canonical_task_reward_static_across_budget": True,
        "canonical_completion_rate_static_across_budget": True,
        "canonical_drop_rate_static_across_budget": True,
        "evaluation_action_distribution_static_across_budget": False,
        "candidate_reward_variation": 0.0,
        "candidate_action_distribution_changed_by_budget": True,
        "candidate_terminal_outcomes_changed_by_budget": False,
        "canonical_policy_effect_summary": {},
        "policy_results": policy_results,
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


def run_fake_pipeline() -> dict[str, object]:
    with mock.patch("src.analysis.reward_emission_evaluation_metric_aggregation_repair.runner.InstrumentedTrainingSession", side_effect=_FakeSession), \
        mock.patch("src.analysis.reward_emission_evaluation_metric_aggregation_repair.runner.evaluate_policy_on_trace_bank_repaired", side_effect=_fake_evaluation_result), \
        mock.patch("src.analysis.reward_emission_evaluation_metric_aggregation_repair.runner.build_policy_effect_after_repair", return_value=_fake_policy_effect_result()):
        payload = run_reward_emission_aggregation_repair()
        write_artifacts(payload)
    return payload


class RewardEmissionEvaluationMetricAggregationRepairIntegrationTests(unittest.TestCase):
    def test_runner_uses_staged_budgets_and_repair_flags(self) -> None:
        payload = run_fake_pipeline()
        self.assertEqual(payload["checkpoint_budgets"], [100, 150, 200, 500])
        self.assertEqual(payload["max_training_budget"], 500)
        self.assertFalse(payload["training_5000_run"])
        self.assertEqual(payload["training_mode"], "cumulative_staged_diagnostic_repair")
        self.assertEqual(payload["policy_affects_reward"], "false")
        self.assertTrue(payload["raw_vs_canonical_reward_reconciliation"]["reward_reconciled"])
        self.assertFalse(payload["raw_reward_event_recovery_blocked"])
        self.assertEqual(_FakeSession.last_instance.calls, [100, 150, 200, 500])

    def test_artifacts_are_written(self) -> None:
        payload = run_fake_pipeline()
        output_dir = Path(payload["figure_manifest"]["figure_directory"]).parent
        expected_files = [
            "reward-emission-aggregation-repair-report.json",
            "reward-emission-aggregation-repair-report.md",
            "repaired-instrumented-checkpoint-metrics.json",
            "reward-event-records.json",
            "terminal-event-records.json",
            "decision-records-summary.json",
            "canonical-task-reconciliation.json",
            "raw-vs-canonical-reward-reconciliation.json",
            "paper-aligned-evaluation-metrics.json",
            "policy-effect-after-repair.json",
            "diagnostic-decision.json",
            "final-repair-summary.md",
            "figure-manifest.json",
        ]
        for name in expected_files:
            self.assertTrue((Path(output_dir) / name).exists(), name)


if __name__ == "__main__":
    unittest.main()
