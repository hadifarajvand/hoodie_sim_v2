from __future__ import annotations

from pathlib import Path

from src.analysis.state_profile_decision_time_integration_recovery.config import OUTPUT_DIR
from src.analysis.state_profile_decision_time_integration_recovery import runner
from tests.unit.test_state_profile_decision_time_integration_recovery_schema import make_repair_payload


class _FakeSession:
    def __init__(self, config, state_representation_profile: str = "deadline_queue_feasibility_v1") -> None:
        self.config = config
        self.state_representation_profile = state_representation_profile
        self.campaign_config = type(
            "CampaignConfig",
            (),
            {
                "seed_bundle": type("SeedBundle", (), {"evaluation_trace_generation_seed": 101})(),
                "evaluation_trace_bank_id": "state-repair-eval-bank",
                "state_representation_profile": state_representation_profile,
            },
        )()
        self.trainer = object()
        self.calls: list[int] = []

    def train_to_budget(self, target_budget: int) -> dict[str, object]:
        self.calls.append(target_budget)
        return {
            "training_budget": target_budget,
            "state_representation_profile": self.state_representation_profile,
            "cumulative_training_episode_count": target_budget,
            "optimizer_step_count": 100 + target_budget,
            "replay_size": 10_000,
            "loss_count": len(self.calls),
            "last_loss": 1.0,
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
        return {
            "policy_name": f"candidate_policy_at_{checkpoint_budget}",
            "checkpoint_budget": checkpoint_budget,
            "evaluation_episode_count": 100,
            "episode_length": 110,
            "evaluation_action_distribution": {"local": 20, "horizontal": 10, "vertical": 70} if checkpoint_budget == 100 else {"local": 5, "horizontal": 5, "vertical": 90},
            "evaluation_decision_count": 100,
            "evaluation_reward_summary": {"canonical_task_count": 100, "completed_task_count": 18 if checkpoint_budget == 100 else 10, "dropped_task_count": 72 if checkpoint_budget == 100 else 85, "pending_at_horizon_count": 10 if checkpoint_budget == 100 else 5, "mean_reward": -8.0 if checkpoint_budget == 100 else -10.0},
            "raw_vs_canonical_terminal_reconciliation": {"terminal_reconciled": True, "terminal_event_coverage_ratio": 1.0},
            "reward_reconciliation_after_terminal_repair": {"reward_reconciled": True, "raw_vs_canonical_reward_delta": 0.0},
            "task_records": {},
        }


def _legacy_report_payload() -> dict[str, object]:
    payload = make_repair_payload()
    legacy = payload["legacy_vs_new_state_profile_comparison"]
    return {
        "feature_id": "070-calibration-metric-consistency-reconciliation-fix",
        "legacy_state_dim": 3,
        "consistent_50_100_comparison": {
            "by_checkpoint": [
                legacy["legacy_candidate_50"],
                legacy["legacy_candidate_100"],
            ]
        },
    }


def test_runner_creates_report_and_figures(monkeypatch) -> None:
    payload = make_repair_payload()

    monkeypatch.setattr(runner, "build_prerequisite_artifacts", lambda: {"feature_070_report": {"verified": True}})
    monkeypatch.setattr(runner, "git_status_paths", lambda: ["src/analysis/state_profile_decision_time_integration_recovery/runner.py"])
    monkeypatch.setattr(runner, "git_staged_paths", lambda: [])
    monkeypatch.setattr(runner, "git_diff_paths", lambda base_ref: ["src/analysis/state_profile_decision_time_integration_recovery/runner.py"])
    monkeypatch.setattr(runner, "load_legacy_state_profile_report", lambda: _legacy_report_payload())
    monkeypatch.setattr(runner, "build_state_feature_coverage_audit", lambda sample_limit: payload["state_feature_coverage_audit"])
    monkeypatch.setattr(runner, "build_state_normalization_audit", lambda audit: payload["state_normalization_audit"])
    monkeypatch.setattr(runner, "StateRepresentationTrainingSession", _FakeSession)
    monkeypatch.setattr(runner, "build_state_representation_policy_effect_comparison", lambda **_: payload["policy_effect_after_state_repair"])

    result = runner.run_state_representation_repair()

    assert result["feature_070_prerequisite_verified"] is True
    assert result["metric_universe_consistency_passed"] is True
    assert result["checkpoint_budgets"] == [50, 100]
    assert result["max_training_budget"] == 100
    assert result["training_5000_run"] is False
    assert result["final_verdict"] == "state_profile_decision_time_integration_ready"
    assert result["diagnostic_decision"]["recommended_next_action"] == "safe_to_proceed_to_reward_function_alignment"
    assert result["policy_effect_after_state_repair"]["any_fixed_policy_completes"] is True
    assert result["action_collapse_diagnostics"]["action_collapse_reduced"] is True
    assert result["selected_action_feasibility_diagnostics"]["selected_action_feasible_ratio_delta"] > 0

    report_dir = OUTPUT_DIR
    expected_files = [
        "state-profile-integration-recovery-report.json",
        "state-profile-integration-recovery-report.md",
        "state-feature-coverage-audit.json",
        "state-normalization-audit.json",
        "legacy-vs-new-state-profile-comparison.json",
        "state-profile-50-100-comparison.json",
        "action-collapse-diagnostics.json",
        "selected-action-feasibility-diagnostics.json",
        "policy-effect-after-state-repair.json",
        "reconciliation-after-state-repair.json",
        "replay-state-alignment-audit.json",
        "diagnostic-decision.json",
        "final-state-profile-integration-summary.md",
        "figure-manifest.json",
    ]
    for filename in expected_files:
        assert (report_dir / filename).exists(), filename

    figure_files = [
        "figure_01_state_feature_group_coverage.png",
        "figure_02_legacy_vs_new_action_distribution.png",
        "figure_03_action_collapse_before_after.png",
        "figure_04_selected_action_feasibility_before_after.png",
        "figure_05_completion_drop_50_vs_100_new_state.png",
    ]
    for filename in figure_files:
        assert (report_dir / "figures" / filename).exists(), filename
