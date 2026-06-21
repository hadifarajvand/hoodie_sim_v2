"""Single paper-compatible metric schema shared by baselines and candidates."""

from __future__ import annotations

from typing import Any

PAPER_COMPATIBLE_METRIC_FIELDS: tuple[str, ...] = (
    "run_id",
    "branch",
    "commit_sha",
    "config_hash",
    "seed_signature",
    "training_budget",
    "evaluation_episode_count",
    "episode_length",
    "calibration_profile",
    "state_representation_profile",
    "policy_name",
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
    "reward_reconciled",
    "terminal_reconciled",
    "raw_vs_canonical_reward_delta",
)


def build_paper_compatible_metric(**values: Any) -> dict[str, Any]:
    """Build a metric row, filling missing fields with None and rejecting unknowns."""

    unknown = set(values) - set(PAPER_COMPATIBLE_METRIC_FIELDS)
    if unknown:
        raise KeyError(f"unknown metric fields: {sorted(unknown)}")
    return {field: values.get(field) for field in PAPER_COMPATIBLE_METRIC_FIELDS}


def validate_metric_schema(row: dict[str, Any]) -> bool:
    """Return True iff row has exactly the schema fields (order-independent)."""

    return set(row) == set(PAPER_COMPATIBLE_METRIC_FIELDS)
