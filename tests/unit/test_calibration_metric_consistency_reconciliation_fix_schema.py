from __future__ import annotations

import json
from pathlib import Path

from src.analysis.calibration_metric_consistency_reconciliation_fix.action_diversity import build_action_path_diversity
from src.analysis.calibration_metric_consistency_reconciliation_fix.config import (
    ALLOWED_DIAGNOSTIC_DECISIONS,
    ALLOWED_FINAL_VERDICTS,
    CalibrationMetricConsistencyConfig,
    EVALUATION_EPISODE_COUNT,
    EPISODE_LENGTH,
    MAX_TRAINING_BUDGET,
    TRAINING_BUDGETS,
)
from src.analysis.calibration_metric_consistency_reconciliation_fix.model import ClaimSafetyStatus, DiagnosticDecision, FigureManifest
from src.analysis.calibration_metric_consistency_reconciliation_fix.reconciliation import build_policy_metric_consistency
from src.analysis.calibration_metric_consistency_reconciliation_fix.universe import build_metric_universe_definitions


def make_task_record(policy_name: str, task_id: int, selected_action: str, terminal_outcome: str, *, raw_reward_event_count: int, raw_terminal_event_count: int, canonical_reward: float) -> dict[str, object]:
    return {
        "trace_id": f"trace-{policy_name}",
        "episode_id": 0,
        "task_id": task_id,
        "selected_action": selected_action,
        "canonical_outcome": terminal_outcome,
        "terminal_outcome": terminal_outcome,
        "raw_reward_event_count": raw_reward_event_count,
        "raw_reward_total": canonical_reward if raw_reward_event_count else 0.0,
        "raw_terminal_event_count": raw_terminal_event_count,
        "canonical_reward": canonical_reward,
        "arrival_slot": task_id - 1,
        "completion_or_drop_slot": task_id,
        "terminal_slot": task_id,
        "latency_slots": 1,
        "timeout_length": 10,
        "task_size": 1.0,
        "processing_density": 0.5,
        "queue_load": 0,
        "pending_evidence": False,
        "reward_event_records": [{"reward_available": True}] if raw_reward_event_count else [],
        "terminal_event_records": [{"terminal_outcome": terminal_outcome}] if raw_terminal_event_count else [],
        "finalized_records": [{"terminal_outcome": terminal_outcome}],
    }


def make_policy_result(policy_name: str, checkpoint_budget: int, selected_actions: list[str]) -> dict[str, object]:
    outcomes = ["completed", "dropped", "dropped"]
    canonical_rewards = [-10.0, -40.0, -40.0]
    task_records = {
        f"{policy_name}-{task_id}": make_task_record(
            policy_name,
            task_id,
            selected_actions[task_id - 1],
            outcomes[task_id - 1],
            raw_reward_event_count=1 if task_id == 1 else 0,
            raw_terminal_event_count=1 if task_id == 1 else 0,
            canonical_reward=canonical_rewards[task_id - 1],
        )
        for task_id in (1, 2, 3)
    }
    action_distribution = {action: selected_actions.count(action) for action in ("local", "horizontal", "vertical")}
    return {
        "policy_name": policy_name,
        "policy_kind": "candidate" if policy_name.startswith("candidate") else "fixed",
        "checkpoint_budget": checkpoint_budget,
        "evaluation_episode_count": 100,
        "episode_length": 110,
        "evaluation_trace_bank_id": "eval-traces",
        "same_evaluation_trace_bank": True,
        "evaluation_action_distribution_source": "evaluation_episodes",
        "evaluation_action_distribution": action_distribution,
        "evaluation_decision_count": 3,
        "completion_path_audit": {
            "execution_completed_event_count": 1,
            "task_completed_event_count": 1,
            "completed_canonical_task_count": 1,
            "deadline_reached_event_count": 2,
            "deadline_expired_event_count": 0,
            "task_dropped_event_count": 2,
            "reward_emitted_event_count": 1,
            "pending_at_horizon_count": 0,
        },
        "reward_event_records": {"record_count": 1},
        "terminal_event_records": {"record_count": 1},
        "task_records": task_records,
    }


def make_synthetic_raw_report() -> dict[str, object]:
    return {
        "calibrated_policy_effect_comparison": {
            "evaluation_trace_bank_id": "eval-traces",
            "evaluation_episode_count": 100,
            "episode_length": 110,
            "candidate_policy_vertical_collapse_in_training_replay_window": False,
            "policy_results": {
                "candidate_policy_at_50": make_policy_result("candidate_policy_at_50", 50, ["vertical", "vertical", "vertical"]),
                "candidate_policy_at_100": make_policy_result("candidate_policy_at_100", 100, ["local", "local", "vertical"]),
                "fixed_local_policy": make_policy_result("fixed_local_policy", 100, ["local", "local", "local"]),
                "fixed_horizontal_policy": make_policy_result("fixed_horizontal_policy", 100, ["horizontal", "horizontal", "horizontal"]),
                "fixed_vertical_policy": make_policy_result("fixed_vertical_policy", 100, ["vertical", "vertical", "vertical"]),
                "random_legal_policy": make_policy_result("random_legal_policy", 100, ["local", "horizontal", "vertical"]),
            },
        }
    }


def fake_estimate_task_action_feasibility(task: dict[str, object]) -> dict[str, object]:
    task_id = int(task["task_id"])
    if task_id == 1:
        local, horizontal, vertical = True, False, True
    elif task_id == 2:
        local, horizontal, vertical = False, True, False
    else:
        local, horizontal, vertical = True, False, False
    return {
        "local_estimated_execution_slots": 1,
        "horizontal_estimated_transmission_slots": 1,
        "horizontal_estimated_execution_slots": 1,
        "horizontal_estimated_total_slots": 2,
        "vertical_estimated_transmission_slots": 1,
        "vertical_estimated_execution_slots": 1,
        "vertical_estimated_total_slots": 2,
        "deadline_slack_for_local": 1 if local else -1,
        "deadline_slack_for_horizontal": 1 if horizontal else -1,
        "deadline_slack_for_vertical": 1 if vertical else -1,
        "local_feasible_before_deadline": local,
        "horizontal_feasible_before_deadline": horizontal,
        "vertical_feasible_before_deadline": vertical,
        "estimate_source": "test",
        "estimate_confidence": "high",
        "missing_fields": [],
    }


def test_schema_constants_and_models():
    assert TRAINING_BUDGETS == (50, 100)
    assert MAX_TRAINING_BUDGET == 100
    assert EVALUATION_EPISODE_COUNT == 100
    assert EPISODE_LENGTH == 110
    assert "safe_to_proceed_to_state_representation_repair" in ALLOWED_DIAGNOSTIC_DECISIONS
    assert "calibration_metric_consistency_reconciliation_ready" in ALLOWED_FINAL_VERDICTS

    config = CalibrationMetricConsistencyConfig()
    assert config.training_budgets == (50, 100)
    assert config.max_training_budget == 100
    assert config.training_5000_run is False

    claim = ClaimSafetyStatus(False, False, False, True)
    assert claim.to_dict()["claim_safety_passed"] is True
    decision = DiagnosticDecision("safe_to_proceed_to_state_representation_repair", "ok", ["evidence"])
    assert decision.to_dict()["recommended_next_action"] == "safe_to_proceed_to_state_representation_repair"
    manifest = FigureManifest("figures", ["a.png", "b.png", "c.png", "d.png", "e.png"], 5, True)
    assert manifest.to_dict()["figure_count"] == 5


def test_metric_universe_definitions_are_explicit():
    universes = build_metric_universe_definitions()
    assert universes["u_full_decisions"]["name"] == "U_full_decisions"
    assert universes["u_unique_tasks"]["name"] == "U_unique_tasks"
    assert universes["u_selected_action_tasks"]["count_source"] == "selected_action_feasible_task_count + selected_action_infeasible_task_count"
    assert universes["feasible_task_count_definition"]["universe"] == "U_selected_action_tasks"
    assert universes["completed_feasible_task_count_definition"]["universe"] == "U_selected_action_tasks"


def test_full_policy_consistency_with_synthetic_payload(monkeypatch):
    from src.analysis.calibration_metric_consistency_reconciliation_fix import action_diversity, reconciliation, runner
    from src.analysis.completion_path_deadline_feasibility_repair import feasibility as base_feasibility

    monkeypatch.setattr(runner, "load_feature_069_raw_report", lambda config=None: make_synthetic_raw_report())
    monkeypatch.setattr(runner, "generate_figures", lambda payload, figures_dir: [])
    monkeypatch.setattr(runner, "git_status_paths", lambda: ["src/analysis/calibration_metric_consistency_reconciliation_fix/runner.py"])
    monkeypatch.setattr(runner, "git_staged_paths", lambda: [])
    monkeypatch.setattr(runner, "git_diff_paths", lambda base_ref: ["src/analysis/calibration_metric_consistency_reconciliation_fix/runner.py"])
    monkeypatch.setattr(reconciliation, "estimate_task_action_feasibility", fake_estimate_task_action_feasibility)
    monkeypatch.setattr(action_diversity, "estimate_task_action_feasibility", fake_estimate_task_action_feasibility)
    monkeypatch.setattr(base_feasibility, "estimate_task_action_feasibility", fake_estimate_task_action_feasibility)

    report = runner.build_calibration_metric_consistency_reconciliation_report()
    candidate_100 = report["consistent_policy_effect_comparison"]["policy_summaries"]["candidate_policy_at_100"]
    assert candidate_100["selected_action_feasible_task_count"] + candidate_100["selected_action_infeasible_task_count"] == candidate_100["unique_task_count"]
    assert candidate_100["completed_selected_action_feasible_count"] + candidate_100["completed_selected_action_infeasible_count"] == candidate_100["completed_task_count"]
    assert candidate_100["dropped_selected_action_feasible_count"] + candidate_100["dropped_selected_action_infeasible_count"] == candidate_100["dropped_task_count"]
    assert candidate_100["reward_reconciliation_status"] == "passed"
    assert candidate_100["terminal_reconciled"] is True
    assert abs(candidate_100["raw_vs_canonical_reward_delta"]) <= 1e-9
    assert report["reward_terminal_reconciliation_fix"]["reward_reconciled"] is True
    assert report["reward_terminal_reconciliation_fix"]["terminal_reconciled"] is True
    assert report["action_path_diversity_check"]["actions_have_different_feasibility"] is True
    assert report["diagnostic_decision"]["recommended_next_action"] == "safe_to_proceed_to_state_representation_repair"
    assert report["final_verdict"] == "calibration_metric_consistency_reconciliation_ready"
