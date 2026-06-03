from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isnan
from typing import Any, Iterable

from .model import ExecutionOutcome, MetricRow


def _safe_average(values: list[float]) -> float | None:
    if not values:
        return None
    return float(sum(values) / len(values))


def completion_rate(completed_count: int, total_task_count: int) -> float:
    return 0.0 if total_task_count <= 0 else float(completed_count / total_task_count)


def timeout_drop_rate(dropped_timeout_count: int, total_task_count: int) -> float:
    return 0.0 if total_task_count <= 0 else float(dropped_timeout_count / total_task_count)


def unavailable_drop_rate(dropped_unavailable_count: int, total_task_count: int) -> float:
    return 0.0 if total_task_count <= 0 else float(dropped_unavailable_count / total_task_count)


def deadline_violation_rate(deadline_violation_count: int, total_task_count: int) -> float:
    return 0.0 if total_task_count <= 0 else float(deadline_violation_count / total_task_count)


def average_delay(delays: Iterable[float | None]) -> float | None:
    values = [float(delay) for delay in delays if delay is not None and not isnan(float(delay))]
    return _safe_average(values)


def average_reward(rewards: Iterable[float | None]) -> float:
    values = [float(reward) for reward in rewards if reward is not None and not isnan(float(reward))]
    return 0.0 if not values else float(sum(values) / len(values))


def total_reward(rewards: Iterable[float | None]) -> float:
    values = [float(reward) for reward in rewards if reward is not None and not isnan(float(reward))]
    return float(sum(values))


def throughput(completed_count: int, scenario_duration: int) -> float:
    return 0.0 if scenario_duration <= 0 else float(completed_count / scenario_duration)


def queue_stability_score(queue_snapshots: Iterable[tuple[int, ...]]) -> float:
    snapshots = [tuple(snapshot) for snapshot in queue_snapshots]
    if not snapshots:
        return 1.0
    averages = [sum(snapshot) / len(snapshot) if snapshot else 0.0 for snapshot in snapshots]
    positive_growth = 0.0
    previous = averages[0]
    for current in averages[1:]:
        growth = current - previous
        if growth > 0:
            positive_growth += growth
        previous = current
    average_queue_length = sum(averages) / len(averages)
    return float(1.0 / (1.0 + average_queue_length + positive_growth))


def build_metric_row(
    *,
    policy: str,
    scenario: str,
    workload: str,
    deadline_pressure: str,
    seed: int | None,
    outcomes: tuple[ExecutionOutcome, ...],
    scenario_duration: int,
) -> MetricRow:
    completed = [outcome for outcome in outcomes if outcome.completed]
    dropped_timeout = [outcome for outcome in outcomes if outcome.dropped_timeout]
    dropped_unavailable = [outcome for outcome in outcomes if outcome.dropped_unavailable]
    violations = [outcome for outcome in outcomes if outcome.deadline_violation]
    illegal = [outcome for outcome in outcomes if outcome.illegal_action_rejected]
    delays = [outcome.delay for outcome in completed]
    rewards = [outcome.reward for outcome in outcomes]
    queue_snapshots = [outcome.queue_length_observations for outcome in outcomes]
    total_task_count = len(outcomes)
    return MetricRow(
        policy=policy,
        scenario=scenario,
        workload=workload,
        deadline_pressure=deadline_pressure,
        seed=seed,
        completed_count=len(completed),
        dropped_timeout_count=len(dropped_timeout),
        dropped_unavailable_count=len(dropped_unavailable),
        deadline_violation_count=len(violations),
        illegal_action_rejection_count=len(illegal),
        average_delay=average_delay(delays),
        average_reward=average_reward(rewards),
        total_reward=total_reward(rewards),
        completion_rate=completion_rate(len(completed), total_task_count),
        timeout_drop_rate=timeout_drop_rate(len(dropped_timeout), total_task_count),
        unavailable_drop_rate=unavailable_drop_rate(len(dropped_unavailable), total_task_count),
        deadline_violation_rate=deadline_violation_rate(len(violations), total_task_count),
        throughput=throughput(len(completed), scenario_duration),
        queue_stability_score=queue_stability_score(queue_snapshots),
        compatibility_mode_used=any(outcome.compatibility_mode_used for outcome in outcomes),
    )
