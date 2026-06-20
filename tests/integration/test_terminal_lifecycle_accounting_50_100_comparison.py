from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

from src.analysis.terminal_lifecycle_accounting_50_100_comparison.config import OUTPUT_DIR
from src.analysis.terminal_lifecycle_accounting_50_100_comparison.runner import run_terminal_lifecycle_comparison, write_artifacts


class _FakeSession:
    last_instance: "_FakeSession | None" = None

    def __init__(self, config) -> None:
        self.config = config
        self.campaign_config = type(
            "Campaign",
            (),
            {
                "seed_bundle": type("SeedBundle", (), {"evaluation_trace_generation_seed": 100})(),
                "evaluation_trace_bank_id": "eval-bank",
            },
        )()
        self.trainer = type(
            "Trainer",
            (),
            {
                "config": type(
                    "TrainerConfig",
                    (),
                    {
                        "training_trace_bank_id": "train-bank",
                        "evaluation_trace_bank_id": "eval-bank",
                        "seed_bundle": type("SeedBundle", (), {"evaluation_trace_generation_seed": 100})(),
                    },
                )()
            },
        )()
        self.calls: list[int] = []
        _FakeSession.last_instance = self

    def train_to_budget(self, target_budget: int) -> dict[str, object]:
        self.calls.append(target_budget)
        return {
            "training_budget": target_budget,
            "cumulative_training_episode_count": target_budget,
            "optimizer_step_count": 100 + len(self.calls),
            "replay_size": 10_000,
            "loss_count": 5 + len(self.calls),
            "last_loss": 1.0 + len(self.calls),
            "loss_finite": True,
            "reward_summary": {"reward_count": 100, "total_reward": -100.0, "mean_reward": -1.0, "pending_at_horizon_count": 0},
            "replay_window_action_distribution": {"local": 0, "horizontal": 0, "vertical": 10_000},
            "replay_window_is_full_training_history": False,
            "replay_window_capacity": 10_000,
            "replay_window_interpretation_warning": True,
            "cumulative_training_action_distribution": {"local": 10, "horizontal": 20, "vertical": 30},
            "training_action_sequence_sample": [{"episode_id": 0, "step_id": 0, "action": "vertical", "legal_action_mask": {"local": True}}],
        }

    def candidate_policy_result(self, *, checkpoint_budget: int) -> dict[str, object]:
        action_distribution = {"local": 0, "horizontal": 0, "vertical": 100} if checkpoint_budget == 100 else {"local": 5, "horizontal": 5, "vertical": 90}
        eval_summary = {
            "evaluation_episode_count": 100,
            "mean_reward": -100.0,
            "completed_task_count": 0,
            "dropped_task_count": 100,
            "pending_at_horizon_count": 0,
            "unknown_task_count": 0,
            "terminal_transition_count": 100,
            "reward_bearing_transition_count": 100,
            "canonical_task_count": 100,
        }
        terminal_recon = {
            "raw_terminal_event_count": 100,
            "canonical_terminal_task_count": 100,
            "terminal_event_coverage_ratio": 1.0,
            "duplicate_terminal_event_count": 0,
            "raw_reward_event_count": 100,
            "canonical_reward_event_count": 100,
            "reward_event_coverage_ratio": 1.0,
            "raw_event_reward_total": -100.0,
            "canonical_task_reward_total": -100.0,
            "raw_vs_canonical_reward_delta": 0.0,
            "terminal_reconciled": True,
            "reward_reconciled": True,
            "raw_reward_event_recovery_blocked": False,
            "terminal_event_recovery_blocked": False,
        }
        policy_effect_stub = {
            "checkpoint_budget": checkpoint_budget,
            "raw_event_reward_total": -100.0,
            "raw_event_reward_count": 100,
            "canonical_task_reward_total": -100.0,
            "canonical_task_reward_count": 100,
            "raw_vs_canonical_reward_delta": 0.0,
            "reward_reconciled": True,
            "reward_reconciliation_tolerance": 1e-9,
            "raw_reward_event_recovery_blocked": False,
            "terminal_event_recovery_blocked": False,
        }
        return {
            "policy_name": f"candidate_policy_at_{checkpoint_budget}",
            "policy_kind": "candidate",
            "checkpoint_budget": checkpoint_budget,
            "evaluation_episode_count": 100,
            "episode_length": 110,
            "evaluation_trace_bank_id": "eval-bank",
            "same_evaluation_trace_bank": True,
            "evaluation_action_distribution_source": "evaluation_episodes",
            "evaluation_action_distribution": action_distribution,
            "evaluation_decision_count": 100,
            "evaluation_action_sequence_sample": [{"trace_id": "trace-0", "episode_id": 0, "task_id": 1, "selected_action": "vertical"}],
            "evaluation_legal_action_mask_distribution": {"local=1|horizontal=1|vertical=1": 100},
            "evaluation_action_by_trace_id": {"trace-0": {"decision_count": 100}},
            "evaluation_action_by_episode_id": {"0": {"decision_count": 100}},
            "decision_records_summary": {"decision_count": 100, "sample_records": [{"trace_id": "trace-0", "episode_id": 0, "task_id": 1, "selected_action": "vertical"}], "evaluation_action_distribution_source": "evaluation_episodes"},
            "terminal_event_records": {"record_count": 100, "sample_records": [{"trace_id": "trace-0", "episode_id": 0, "task_id": 1}], "recovered_from_finalized_tasks": True},
            "reward_event_records": {"record_count": 100, "sample_records": [{"trace_id": "trace-0", "episode_id": 0, "task_id": 1, "raw_reward": -1.0}], "reward_available_count": 100, "raw_reward_event_recovery_blocked": False},
            "task_records": {},
            "episode_summaries": [{"episode_id": 0, "trace_id": "trace-0", "decision_count": 100, "terminal_task_count": 100, "completion_count": 0, "drop_count": 100, "pending_count": 0, "unknown_count": 0, "raw_reward_event_count": 100, "raw_reward_total": -100.0, "canonical_reward_total": -100.0, "reward_recovered": True}],
            "reward_reconciliation_tolerance": 1e-9,
            "raw_reward_event_recovery_blocked": False,
            "terminal_event_recovery_blocked": False,
            "raw_reward_event_count": 100,
            "raw_reward_total": -100.0,
            "raw_terminal_event_count": 100,
            "episode_reward_totals": [-100.0],
            "candidate_policy_vertical_share": 1.0 if checkpoint_budget == 100 else 0.9,
            "evaluation_reward_summary": eval_summary,
            "terminal_event_classification": {"overall": {"terminal_outcome_event_count": 100, "lifecycle_only_event_count": 100, "reward_event_count": 100, "pending_event_count": 0, "event_type_counts": {"task_dropped": 100, "reward_emitted": 100, "deadline_reached": 100, "deadline_expired": 100}}},
            "canonical_terminal_task_summary": {"overall": {"canonical_task_count": 100, "canonical_terminal_task_count": 100, "canonical_completion_count": 0, "canonical_drop_count": 100, "canonical_pending_count": 0, "canonical_unknown_count": 0, "raw_terminal_event_count": 100, "raw_reward_emission_count": 100, "raw_event_reward_total": -100.0, "raw_event_reward_count": 100, "canonical_task_reward_total": -100.0, "canonical_task_reward_count": 100, "raw_vs_canonical_reward_delta": 0.0, "duplicate_terminal_event_count": 0, "duplicate_reward_event_count": 0, "double_count_detected": False, "canonical_completion_ratio": 0.0, "canonical_drop_ratio": 1.0, "canonical_deadline_violation_ratio": 1.0, "canonical_pending_ratio": 0.0, "canonical_mean_completion_latency_slots": None, "canonical_mean_drop_latency_slots": 4.0, "canonical_mean_terminal_latency_slots": 4.0, "canonical_reward_per_task": -1.0, "canonical_reward_per_decision": -1.0, "canonical_tasks_per_decision": 1.0}},
            "raw_vs_canonical_terminal_reconciliation": terminal_recon,
            "reward_reconciliation_after_terminal_repair": policy_effect_stub,
            "completion_path_audit": {"execution_completed_event_count": 0, "task_completed_event_count": 0, "completed_canonical_task_count": 0, "deadline_reached_event_count": 100, "deadline_expired_event_count": 100, "task_dropped_event_count": 100, "reward_emitted_event_count": 100, "pending_at_horizon_count": 0, "execution_completed_but_no_task_completed_detected": False, "task_completed_but_no_reward_detected": False, "deadline_reached_then_task_dropped_duplicate_detected": True, "reward_emitted_without_terminal_outcome_detected": False, "terminal_outcome_without_reward_detected": False},
            "paper_aligned_diagnostic_metrics": {"checkpoint_budget": checkpoint_budget, "canonical_completion_ratio": 0.0, "canonical_drop_ratio": 1.0, "canonical_deadline_violation_ratio": 1.0, "canonical_pending_ratio": 0.0, "canonical_mean_completion_latency_slots": None, "canonical_mean_drop_latency_slots": 4.0, "canonical_mean_terminal_latency_slots": 4.0, "canonical_reward_per_task": -1.0, "canonical_reward_per_decision": -1.0, "canonical_tasks_per_decision": 1.0, "reward_reconciliation_status": "passed", "raw_reward_event_coverage_ratio": 1.0, "terminal_event_coverage_ratio": 1.0},
        }


def _fake_policy_effect_result() -> dict[str, object]:
    policy_results = {
        "candidate_policy_at_50": _FakeSession(None).candidate_policy_result(checkpoint_budget=50),
        "candidate_policy_at_100": _FakeSession(None).candidate_policy_result(checkpoint_budget=100),
        "fixed_local_policy": _FakeSession(None).candidate_policy_result(checkpoint_budget=100),
        "fixed_horizontal_policy": _FakeSession(None).candidate_policy_result(checkpoint_budget=100),
        "fixed_vertical_policy": _FakeSession(None).candidate_policy_result(checkpoint_budget=100),
        "random_legal_policy": _FakeSession(None).candidate_policy_result(checkpoint_budget=100),
    }
    return {
        "evaluation_trace_bank_id": "eval-bank",
        "evaluation_episode_count": 100,
        "episode_length": 110,
        "candidate_policy_vertical_collapse_in_evaluation": True,
        "candidate_policy_vertical_collapse_in_training_replay_window": True,
        "policy_affects_reward": "false",
        "policy_affects_terminal_outcomes": "false",
        "evaluation_reward_static_after_terminal_repair": True,
        "evaluation_action_distribution_static_across_budget": False,
        "raw_event_reward_static_across_budget": False,
        "canonical_task_reward_static_across_budget": True,
        "canonical_completion_rate_static_across_budget": True,
        "canonical_drop_rate_static_across_budget": True,
        "policy_results": policy_results,
        "candidate_reward_variation": 0.0,
        "candidate_action_distribution_changed_by_budget": False,
        "candidate_terminal_outcomes_changed_by_budget": False,
        "canonical_policy_effect_summary": {},
    }


def run_fake_pipeline() -> dict[str, object]:
    with mock.patch("src.analysis.terminal_lifecycle_accounting_50_100_comparison.runner.TerminalLifecycleTrainingSession", side_effect=_FakeSession), \
        mock.patch("src.analysis.terminal_lifecycle_accounting_50_100_comparison.runner.build_policy_effect_after_terminal_repair", side_effect=lambda **_: _fake_policy_effect_result()):
        payload = run_terminal_lifecycle_comparison()
        write_artifacts(payload)
    return payload


class TerminalLifecycleAccounting50_100ComparisonIntegrationTests(unittest.TestCase):
    def test_runner_uses_staged_budgets_and_repair_flags(self) -> None:
        payload = run_fake_pipeline()
        self.assertEqual(payload["checkpoint_budgets"], [50, 100])
        self.assertEqual(payload["max_training_budget"], 100)
        self.assertFalse(payload["training_5000_run"])
        self.assertFalse(payload["training_rerun_from_scratch"])
        self.assertEqual(payload["training_mode"], "cumulative_staged_50_100_comparison")
        self.assertTrue(payload["raw_vs_canonical_terminal_reconciliation"]["overall"]["terminal_reconciled"])
        self.assertTrue(payload["reward_reconciliation_after_terminal_repair"]["overall"]["reward_reconciled"])
        self.assertEqual(payload["diagnostic_decision"]["recommended_next_action"], "fix_completion_path_next")
        self.assertEqual(payload["checkpoint_metrics"][0]["evaluation_policy_result"]["decision_records_summary"]["evaluation_action_distribution_source"], "evaluation_episodes")
        self.assertTrue(payload["checkpoint_metrics"][0]["training_state"]["replay_window_interpretation_warning"])
        self.assertEqual(payload["checkpoint_metrics"][0]["training_state"]["replay_window_capacity"], 10_000)
        self.assertFalse(payload["reward_function_modified"])
        self.assertFalse(payload["environment_semantics_modified"])
        self.assertFalse(payload["policy_modified"])
        self.assertFalse(payload["dal_modified"])
        self.assertFalse(payload["dependencies_modified"])

    def test_artifacts_are_written(self) -> None:
        payload = run_fake_pipeline()
        output_dir = Path(payload["figure_manifest"]["figure_directory"]).parent
        expected_files = [
            "terminal-lifecycle-repair-report.json",
            "terminal-lifecycle-repair-report.md",
            "checkpoint-50-100-comparison.json",
            "terminal-event-classification.json",
            "canonical-terminal-task-summary.json",
            "raw-vs-canonical-terminal-reconciliation.json",
            "reward-reconciliation-after-terminal-repair.json",
            "completion-path-audit.json",
            "policy-effect-50-100-after-terminal-repair.json",
            "paper-aligned-50-100-metrics.json",
            "diagnostic-decision.json",
            "final-terminal-lifecycle-summary.md",
            "figure-manifest.json",
        ]
        for name in expected_files:
            self.assertTrue((Path(output_dir) / name).exists(), name)


if __name__ == "__main__":
    unittest.main()
