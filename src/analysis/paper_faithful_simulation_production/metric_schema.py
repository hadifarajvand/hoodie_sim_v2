"""Paper-compatible metric schema for the production simulation pipeline."""

from __future__ import annotations

from typing import Any

PAPER_COMPATIBLE_METRIC_FIELDS: tuple[str, ...] = (
    "run_id",
    "branch",
    "commit_sha",
    "config_hash",
    "seed_signature",
    "simulation_profile",
    "calibration_profile",
    "state_representation_profile",
    "reconciliation_profile",
    "policy_name",
    "training_budget",
    "evaluation_episode_count",
    "episode_length",
    "decision_count",
    "unique_task_count",
    "completed_count",
    "dropped_count",
    "pending_count",
    "completion_ratio",
    "drop_ratio",
    "deadline_violation_ratio",
    "average_latency_slots",
    "average_completion_latency_slots",
    "average_drop_latency_slots",
    "reward_total",
    "reward_mean",
    "reward_per_task",
    "reward_per_decision",
    "action_local_count",
    "action_horizontal_count",
    "action_vertical_count",
    "action_local_ratio",
    "action_horizontal_ratio",
    "action_vertical_ratio",
    "selected_action_feasible_count",
    "selected_action_infeasible_count",
    "selected_action_feasible_ratio",
    "queue_pressure_mean",
    "terminal_event_count",
    "reward_event_count",
    "recovered_horizon_reward_event_count",
    "horizon_finalized_terminal_count",
    "reward_reconciled",
    "terminal_reconciled",
    "raw_vs_canonical_reward_delta",
    # Energy/cost are not modeled by the current environment; reported as None
    # with an explicit status (energy_metric_status = not_implemented).
    "energy_total",
    "energy_mean",
    "cost_total",
    "cost_mean",
)

ENERGY_METRIC_STATUS = "not_implemented"


def build_metric(**values: Any) -> dict[str, Any]:
    unknown = set(values) - set(PAPER_COMPATIBLE_METRIC_FIELDS)
    if unknown:
        raise KeyError(f"unknown metric fields: {sorted(unknown)}")
    return {field: values.get(field) for field in PAPER_COMPATIBLE_METRIC_FIELDS}


def validate_metric_schema(row: dict[str, Any]) -> bool:
    return set(row) == set(PAPER_COMPATIBLE_METRIC_FIELDS)
