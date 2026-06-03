from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable

from .model import MetricRow


def aggregate_by_policy(rows: Iterable[MetricRow]) -> tuple[MetricRow, ...]:
    grouped: dict[str, list[MetricRow]] = defaultdict(list)
    for row in rows:
        grouped[row.policy].append(row)
    return tuple(_aggregate_group(policy, items, scenario="ALL", workload="ALL", deadline_pressure="ALL", seed=None) for policy, items in sorted(grouped.items()))


def aggregate_by_policy_and_scenario(rows: Iterable[MetricRow]) -> tuple[MetricRow, ...]:
    return tuple(
        _aggregate_group(key[0], items, scenario=key[1], workload="ALL", deadline_pressure="ALL", seed=None)
        for key, items in sorted(_group(rows, lambda row: (row.policy, row.scenario)).items())
    )


def aggregate_by_policy_and_workload(rows: Iterable[MetricRow]) -> tuple[MetricRow, ...]:
    return tuple(
        _aggregate_group(key[0], items, scenario="ALL", workload=key[1], deadline_pressure="ALL", seed=None)
        for key, items in sorted(_group(rows, lambda row: (row.policy, row.workload)).items())
    )


def aggregate_by_policy_and_deadline_pressure(rows: Iterable[MetricRow]) -> tuple[MetricRow, ...]:
    return tuple(
        _aggregate_group(key[0], items, scenario="ALL", workload="ALL", deadline_pressure=key[1], seed=None)
        for key, items in sorted(_group(rows, lambda row: (row.policy, row.deadline_pressure)).items())
    )


def _group(rows: Iterable[MetricRow], key_fn):
    grouped: dict[tuple[str, str], list[MetricRow]] = defaultdict(list)
    for row in rows:
        grouped[key_fn(row)].append(row)
    return grouped


def _aggregate_group(
    policy: str,
    items: list[MetricRow],
    *,
    scenario: str,
    workload: str,
    deadline_pressure: str,
    seed: int | None,
) -> MetricRow:
    count = len(items)
    completed = sum(item.completed_count for item in items)
    dropped_timeout = sum(item.dropped_timeout_count for item in items)
    dropped_unavailable = sum(item.dropped_unavailable_count for item in items)
    deadline_violations = sum(item.deadline_violation_count for item in items)
    illegal = sum(item.illegal_action_rejection_count for item in items)
    average_delay_values = [item.average_delay for item in items if item.average_delay is not None]
    average_reward_values = [item.average_reward for item in items]
    total_reward_values = [item.total_reward for item in items]
    throughput_values = [item.throughput for item in items]
    queue_scores = [item.queue_stability_score for item in items]
    return MetricRow(
        policy=policy,
        scenario=scenario,
        workload=workload,
        deadline_pressure=deadline_pressure,
        seed=seed,
        completed_count=completed,
        dropped_timeout_count=dropped_timeout,
        dropped_unavailable_count=dropped_unavailable,
        deadline_violation_count=deadline_violations,
        illegal_action_rejection_count=illegal,
        average_delay=(sum(average_delay_values) / len(average_delay_values)) if average_delay_values else None,
        average_reward=sum(average_reward_values) / count if count else 0.0,
        total_reward=sum(total_reward_values),
        completion_rate=(completed / sum(item.completed_count + item.dropped_timeout_count + item.dropped_unavailable_count for item in items)) if items else 0.0,
        timeout_drop_rate=(dropped_timeout / sum(item.completed_count + item.dropped_timeout_count + item.dropped_unavailable_count for item in items)) if items else 0.0,
        unavailable_drop_rate=(dropped_unavailable / sum(item.completed_count + item.dropped_timeout_count + item.dropped_unavailable_count for item in items)) if items else 0.0,
        deadline_violation_rate=(deadline_violations / sum(item.completed_count + item.dropped_timeout_count + item.dropped_unavailable_count for item in items)) if items else 0.0,
        throughput=sum(throughput_values) / count if count else 0.0,
        queue_stability_score=sum(queue_scores) / count if count else 1.0,
        compatibility_mode_used=any(item.compatibility_mode_used for item in items),
    )
