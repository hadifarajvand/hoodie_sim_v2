"""Integrated medium-smoke simulation runner for the production pipeline.

Reuses the proven Feature 072 training/evaluation harness and the Feature
080/081 horizon-aware recovered reconciliation. Trains a single candidate policy
cumulatively to the bounded budgets [50, 100, 200, 300], evaluating at each
checkpoint, and evaluates the four fixed baselines once. No environment, reward,
policy, or DAL semantics are modified.
"""

from __future__ import annotations

from typing import Any

from src.analysis.completion_path_deadline_feasibility_repair.feasibility import (
    build_task_feasibility_summary,
)
from src.analysis.full_training_reproduction_campaign.replay import (
    STATE_REPRESENTATION_PROFILE_DEADLINE_QUEUE_FEASIBILITY_V1,
)
from src.analysis.paper_faithful_simulation_production.metric_schema import build_metric
from src.analysis.paper_faithful_simulation_production.profiles import ProductionProfile
from src.analysis.paper_faithful_simulation_production_pipeline.reconciliation import (
    REWARD_RECONCILIATION_TOLERANCE,
    horizon_aware_recovered_reconciliation,
)
from src.analysis.state_profile_decision_time_integration_recovery.config import (
    StateRepresentationRepairConfig,
)
from src.analysis.state_profile_decision_time_integration_recovery.policy_probe import (
    StateRepresentationTrainingSession,
)

_FEASIBLE_KEYS = {
    "local": "local_feasible_before_deadline",
    "compute_local": "local_feasible_before_deadline",
    "horizontal": "horizontal_feasible_before_deadline",
    "offload_horizontal": "horizontal_feasible_before_deadline",
    "vertical": "vertical_feasible_before_deadline",
    "offload_vertical": "vertical_feasible_before_deadline",
}


def _mean(values: list[float]) -> float | None:
    return (sum(values) / len(values)) if values else None


def _metric_row(
    *, policy_name: str, training_budget: int | None, evaluation_result: dict[str, Any],
    profile: ProductionProfile, commit: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    task_records = dict(evaluation_result.get("task_records", {}))
    recon = horizon_aware_recovered_reconciliation(task_records, tolerance=REWARD_RECONCILIATION_TOLERANCE)
    dist = dict(evaluation_result.get("evaluation_action_distribution", {}))
    total_actions = sum(int(v) for v in dist.values())
    decision_count = int(evaluation_result.get("evaluation_decision_count", total_actions))

    completed, dropped, pending = recon["completed_count"], recon["dropped_count"], recon["pending_at_horizon_count"]
    unique = completed + dropped + pending
    comp_lat = [float(r["latency_slots"]) for r in task_records.values() if r.get("terminal_outcome") == "completed" and r.get("latency_slots") is not None]
    drop_lat = [float(r["latency_slots"]) for r in task_records.values() if r.get("terminal_outcome") == "dropped" and r.get("latency_slots") is not None]

    feas = build_task_feasibility_summary(task_records, record_sample_limit=10)
    by_key = feas.get("records_by_task_key", {})
    feasible = infeasible = 0
    for key, record in task_records.items():
        fz = dict(by_key.get(key, {}))
        action = str(record.get("selected_action") or fz.get("selected_action") or "")
        if _FEASIBLE_KEYS.get(action) and fz.get(_FEASIBLE_KEYS[action]):
            feasible += 1
        else:
            infeasible += 1

    reward_total = recon["canonical_reward_total"]
    row = build_metric(
        run_id=f"PFSP-{policy_name}-b{training_budget}",
        branch="paper-faithful-simulation-production-implementation",
        commit_sha=commit,
        config_hash=None,
        seed_signature="paper_faithful_base:eval_seed_base",
        simulation_profile=profile.simulation_profile,
        calibration_profile=profile.calibration_profile,
        state_representation_profile=profile.state_representation_profile,
        reconciliation_profile=profile.reconciliation_profile,
        policy_name=policy_name,
        training_budget=training_budget,
        evaluation_episode_count=profile.evaluation_episode_count,
        episode_length=profile.episode_length,
        decision_count=decision_count,
        unique_task_count=unique,
        completed_count=completed,
        dropped_count=dropped,
        pending_count=pending,
        completion_ratio=(completed / unique) if unique else 0.0,
        drop_ratio=(dropped / unique) if unique else 0.0,
        deadline_violation_ratio=(dropped / unique) if unique else 0.0,
        average_latency_slots=_mean(comp_lat + drop_lat),
        average_completion_latency_slots=_mean(comp_lat),
        average_drop_latency_slots=_mean(drop_lat),
        reward_total=reward_total,
        reward_mean=(reward_total / unique) if unique else 0.0,
        reward_per_task=(reward_total / unique) if unique else 0.0,
        reward_per_decision=(reward_total / decision_count) if decision_count else 0.0,
        action_local_count=int(dist.get("local", 0)),
        action_horizontal_count=int(dist.get("horizontal", 0)),
        action_vertical_count=int(dist.get("vertical", 0)),
        action_local_ratio=(int(dist.get("local", 0)) / total_actions) if total_actions else None,
        action_horizontal_ratio=(int(dist.get("horizontal", 0)) / total_actions) if total_actions else None,
        action_vertical_ratio=(int(dist.get("vertical", 0)) / total_actions) if total_actions else None,
        selected_action_feasible_count=feasible,
        selected_action_infeasible_count=infeasible,
        selected_action_feasible_ratio=(feasible / unique) if unique else 0.0,
        queue_pressure_mean=_mean([float(r.get("queue_load", 0) or 0) for r in task_records.values()]),
        terminal_event_count=recon["canonical_terminal_task_count"],
        reward_event_count=recon["raw_reward_event_count"],
        recovered_horizon_reward_event_count=recon["recovered_horizon_reward_event_count"],
        horizon_finalized_terminal_count=recon["horizon_finalized_terminal_count"],
        reward_reconciled=recon["reward_reconciled"],
        terminal_reconciled=recon["terminal_reconciled"],
        raw_vs_canonical_reward_delta=recon["raw_vs_canonical_reward_delta"],
        energy_total=None,
        energy_mean=None,
        cost_total=None,
        cost_mean=None,
    )
    detail = {
        "policy_name": policy_name, "training_budget": training_budget,
        "terminal_event_coverage_ratio": recon["terminal_event_coverage_ratio"],
        "raw_plus_recovered_reward_total": recon["raw_plus_recovered_reward_total"],
        "canonical_reward_total": recon["canonical_reward_total"],
        "raw_vs_canonical_reward_delta": recon["raw_vs_canonical_reward_delta"],
        "recovered_horizon_reward_event_count": recon["recovered_horizon_reward_event_count"],
        "horizon_finalized_terminal_count": recon["horizon_finalized_terminal_count"],
    }
    return row, detail


def run_medium_smoke(profile: ProductionProfile, commit: str) -> dict[str, Any]:
    cfg = StateRepresentationRepairConfig()
    session = StateRepresentationTrainingSession(
        config=cfg, state_representation_profile=STATE_REPRESENTATION_PROFILE_DEADLINE_QUEUE_FEASIBILITY_V1,
    )
    rows: list[dict[str, Any]] = []
    details: list[dict[str, Any]] = []
    budgets_executed: list[int] = []

    for budget in profile.training_budgets:
        session.train_to_budget(budget)
        budgets_executed.append(budget)
        result = session.candidate_policy_result(checkpoint_budget=budget)
        row, detail = _metric_row(
            policy_name=f"candidate_learned_policy_at_{budget}", training_budget=budget,
            evaluation_result=result, profile=profile, commit=commit,
        )
        rows.append(row)
        details.append(detail)

    fixed_results = session.fixed_policy_results()
    for fixed_name, fixed_result in fixed_results.items():
        row, detail = _metric_row(
            policy_name=fixed_name, training_budget=None,
            evaluation_result=fixed_result, profile=profile, commit=commit,
        )
        rows.append(row)
        details.append(detail)

    return {"rows": rows, "details": details, "budgets_executed": sorted(set(budgets_executed))}
