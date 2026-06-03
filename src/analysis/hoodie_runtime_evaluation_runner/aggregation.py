from __future__ import annotations

from collections import defaultdict

from .model import MetricRow


def _combine_rows(rows: tuple[MetricRow, ...], *, policy: str, scenario: str, workload: str, deadline_pressure: str) -> MetricRow:
    if not rows:
        raise ValueError("rows must be non-empty")
    completed = sum(row.completed_count for row in rows)
    timeout_dropped = sum(row.dropped_timeout_count for row in rows)
    unavailable_dropped = sum(row.dropped_unavailable_count for row in rows)
    deadline_violations = sum(row.deadline_violation_count for row in rows)
    illegal_action_rejections = sum(row.illegal_action_rejection_count for row in rows)
    total = completed + timeout_dropped + unavailable_dropped

    weighted_completion_delay = sum((row.task_completion_delay or 0.0) * row.completed_count for row in rows if row.task_completion_delay is not None)
    task_completion_delay = float(weighted_completion_delay / completed) if completed else None
    total_reward = sum(row.total_reward for row in rows)
    average_reward = float(total_reward / total) if total else 0.0
    queue_stability = sum(row.queue_stability_score * max(1, row.completed_count + row.dropped_timeout_count + row.dropped_unavailable_count) for row in rows)
    queue_denominator = sum(max(1, row.completed_count + row.dropped_timeout_count + row.dropped_unavailable_count) for row in rows)
    compatibility_mode_used = any(row.compatibility_mode_used for row in rows)
    task_drop_ratio = float((timeout_dropped + unavailable_dropped) / total) if total else 0.0
    return MetricRow(
        policy=policy,
        scenario=scenario,
        workload=workload,
        deadline_pressure=deadline_pressure,
        seed=None,
        completed_count=completed,
        dropped_timeout_count=timeout_dropped,
        dropped_unavailable_count=unavailable_dropped,
        deadline_violation_count=deadline_violations,
        illegal_action_rejection_count=illegal_action_rejections,
        task_completion_delay=task_completion_delay,
        task_drop_ratio=task_drop_ratio,
        average_delay=task_completion_delay,
        drop_ratio=task_drop_ratio,
        completion_rate=float(completed / total) if total else 0.0,
        timeout_drop_rate=float(timeout_dropped / total) if total else 0.0,
        unavailable_drop_rate=float(unavailable_dropped / total) if total else 0.0,
        deadline_violation_rate=float(deadline_violations / total) if total else 0.0,
        average_reward=average_reward,
        total_reward=float(total_reward),
        throughput=float(completed / total) if total else 0.0,
        queue_stability_score=float(queue_stability / queue_denominator) if queue_denominator else 1.0,
        compatibility_mode_used=compatibility_mode_used,
    )


def aggregate_by_policy(rows: tuple[MetricRow, ...]) -> tuple[MetricRow, ...]:
    grouped: dict[str, list[MetricRow]] = defaultdict(list)
    for row in rows:
        grouped[row.policy].append(row)
    return tuple(
        _combine_rows(tuple(grouped[policy]), policy=policy, scenario="all", workload="all", deadline_pressure="all")
        for policy in sorted(grouped)
    )


def aggregate_by_policy_and_scenario(rows: tuple[MetricRow, ...]) -> tuple[MetricRow, ...]:
    grouped: dict[tuple[str, str], list[MetricRow]] = defaultdict(list)
    for row in rows:
        grouped[(row.policy, row.scenario)].append(row)
    return tuple(
        _combine_rows(tuple(grouped[key]), policy=key[0], scenario=key[1], workload="all", deadline_pressure="all")
        for key in sorted(grouped)
    )


def aggregate_by_policy_and_workload(rows: tuple[MetricRow, ...]) -> tuple[MetricRow, ...]:
    grouped: dict[tuple[str, str], list[MetricRow]] = defaultdict(list)
    for row in rows:
        grouped[(row.policy, row.workload)].append(row)
    return tuple(
        _combine_rows(tuple(grouped[key]), policy=key[0], scenario="all", workload=key[1], deadline_pressure="all")
        for key in sorted(grouped)
    )


def aggregate_by_policy_and_deadline_pressure(rows: tuple[MetricRow, ...]) -> tuple[MetricRow, ...]:
    grouped: dict[tuple[str, str], list[MetricRow]] = defaultdict(list)
    for row in rows:
        grouped[(row.policy, row.deadline_pressure)].append(row)
    return tuple(
        _combine_rows(tuple(grouped[key]), policy=key[0], scenario="all", workload="all", deadline_pressure=key[1])
        for key in sorted(grouped)
    )
