from __future__ import annotations

from statistics import mean

from .model import ExecutionOutcome, MetricRow


def completion_rate(completed: int, total: int) -> float:
    return float(completed / total) if total else 0.0


def timeout_drop_rate(timeout_dropped: int, total: int) -> float:
    return float(timeout_dropped / total) if total else 0.0


def unavailable_drop_rate(unavailable_dropped: int, total: int) -> float:
    return float(unavailable_dropped / total) if total else 0.0


def deadline_violation_rate(violations: int, total: int) -> float:
    return float(violations / total) if total else 0.0


def task_completion_delay(delays: list[float]) -> float | None:
    return float(mean(delays)) if delays else None


def task_drop_ratio(timeout_dropped: int, unavailable_dropped: int, total: int) -> float:
    if not total:
        return 0.0
    return float((timeout_dropped + unavailable_dropped) / total)


def average_reward(rewards: list[float]) -> float:
    return float(mean(rewards)) if rewards else 0.0


def total_reward(rewards: list[float]) -> float:
    return float(sum(rewards))


def throughput(completed_count: int, total_count: int) -> float:
    return float(completed_count / total_count) if total_count else 0.0


def queue_stability_score(queue_observations: list[tuple[int, ...]]) -> float:
    if not queue_observations:
        return 1.0
    average_queue_length = mean(sum(snapshot) / max(1, len(snapshot)) for snapshot in queue_observations)
    positive_growth = 0
    for previous, current in zip(queue_observations, queue_observations[1:]):
        if sum(current) > sum(previous):
            positive_growth += 1
    return float(1 / (1 + average_queue_length + positive_growth))


def build_metric_row(*, policy: str, scenario: str, workload: str, deadline_pressure: str, seed: int | None, outcomes: tuple[ExecutionOutcome, ...]) -> MetricRow:
    total = len(outcomes)
    completed = sum(1 for outcome in outcomes if outcome.completed)
    timeout_dropped = sum(1 for outcome in outcomes if outcome.dropped_timeout)
    unavailable_dropped = sum(1 for outcome in outcomes if outcome.dropped_unavailable)
    deadline_violations = sum(1 for outcome in outcomes if outcome.deadline_violation)
    illegal_action_rejections = sum(1 for outcome in outcomes if outcome.illegal_action_rejected)
    delays = [outcome.delay for outcome in outcomes if outcome.delay is not None]
    rewards = [float(outcome.reward) for outcome in outcomes if outcome.reward is not None]
    queue_observations = [outcome.queue_length_observations for outcome in outcomes]
    completion_delay = task_completion_delay(delays)
    drop_ratio = task_drop_ratio(timeout_dropped, unavailable_dropped, total)
    return MetricRow(
        policy=policy,
        scenario=scenario,
        workload=workload,
        deadline_pressure=deadline_pressure,
        seed=seed,
        completed_count=completed,
        dropped_timeout_count=timeout_dropped,
        dropped_unavailable_count=unavailable_dropped,
        deadline_violation_count=deadline_violations,
        illegal_action_rejection_count=illegal_action_rejections,
        task_completion_delay=completion_delay,
        task_drop_ratio=drop_ratio,
        average_delay=completion_delay,
        drop_ratio=drop_ratio,
        completion_rate=completion_rate(completed, total),
        timeout_drop_rate=timeout_drop_rate(timeout_dropped, total),
        unavailable_drop_rate=unavailable_drop_rate(unavailable_dropped, total),
        deadline_violation_rate=deadline_violation_rate(deadline_violations, total),
        average_reward=average_reward(rewards),
        total_reward=total_reward(rewards),
        throughput=throughput(completed, total),
        queue_stability_score=queue_stability_score(queue_observations),
        compatibility_mode_used=any(outcome.compatibility_mode_used for outcome in outcomes),
    )
