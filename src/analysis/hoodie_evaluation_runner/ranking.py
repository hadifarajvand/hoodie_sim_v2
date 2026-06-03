from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .model import MetricRow, RankingRow


HIGHER_IS_BETTER = {
    "completion_rate",
    "average_reward",
    "total_reward",
    "throughput",
    "queue_stability_score",
}

LOWER_IS_BETTER = {
    "average_delay",
    "timeout_drop_rate",
    "unavailable_drop_rate",
    "deadline_violation_rate",
    "illegal_action_rejection_count",
}

RANKING_METRICS = tuple(sorted(HIGHER_IS_BETTER | LOWER_IS_BETTER))


def build_metric_rankings(rows: Iterable[MetricRow]) -> dict[str, tuple[RankingRow, ...]]:
    row_list = list(rows)
    rankings: dict[str, tuple[RankingRow, ...]] = {}
    for metric in RANKING_METRICS:
        rankings[metric] = tuple(_rank_metric(metric, row_list))
    return rankings


def _rank_metric(metric: str, rows: list[MetricRow]) -> list[RankingRow]:
    direction = "higher_is_better" if metric in HIGHER_IS_BETTER else "lower_is_better"
    sortable = []
    for row in rows:
        value = getattr(row, metric)
        if value is None:
            value = float("nan")
        sortable.append((row.policy, float(value), row))
    sortable.sort(key=lambda item: _sort_key(metric, item[2]))
    ranked: list[RankingRow] = []
    for index, (_policy, value, row) in enumerate(sortable, start=1):
        ranked.append(
            RankingRow(
                metric=metric,
                rank=index,
                policy=row.policy,
                value=float(value),
                direction=direction,
                tie_break_trace=(
                    f"average_delay={row.average_delay}",
                    f"deadline_violation_rate={row.deadline_violation_rate}",
                    f"timeout_drop_rate={row.timeout_drop_rate}",
                    f"policy={row.policy}",
                ),
            )
        )
    return ranked


def _sort_key(metric: str, row: MetricRow) -> tuple:
    metric_value = getattr(row, metric)
    if metric_value is None:
        metric_value = float("inf") if metric in LOWER_IS_BETTER else float("-inf")
    if metric in HIGHER_IS_BETTER:
        return (
            -float(metric_value),
            float(row.average_delay if row.average_delay is not None else float("inf")),
            float(row.deadline_violation_rate),
            float(row.timeout_drop_rate),
            row.policy,
        )
    return (
        float(metric_value),
        float(row.average_delay if row.average_delay is not None else float("inf")),
        float(row.deadline_violation_rate),
        float(row.timeout_drop_rate),
        row.policy,
    )
