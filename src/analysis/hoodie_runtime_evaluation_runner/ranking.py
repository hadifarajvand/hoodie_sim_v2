from __future__ import annotations

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


def _sort_key(metric: str, row: MetricRow) -> tuple[float, float, float, float, str]:
    average_delay = row.average_delay if row.average_delay is not None else float("inf")
    deadline_violation_rate = row.deadline_violation_rate
    timeout_drop_rate = row.timeout_drop_rate
    if metric in HIGHER_IS_BETTER:
        return (-row_value(metric, row), average_delay, deadline_violation_rate, timeout_drop_rate, row.policy)
    return (row_value(metric, row), average_delay, deadline_violation_rate, timeout_drop_rate, row.policy)


def row_value(metric: str, row: MetricRow) -> float:
    value = getattr(row, metric)
    return float(value if value is not None else 0.0)


def build_metric_rankings(rows: tuple[MetricRow, ...]) -> dict[str, tuple[RankingRow, ...]]:
    rankings: dict[str, tuple[RankingRow, ...]] = {}
    for metric in sorted(HIGHER_IS_BETTER | LOWER_IS_BETTER):
        direction = "higher_is_better" if metric in HIGHER_IS_BETTER else "lower_is_better"
        sorted_rows = sorted(rows, key=lambda row: _sort_key(metric, row))
        ranking_rows = tuple(
            RankingRow(
                metric=metric,
                rank=index + 1,
                policy=row.policy,
                value=row_value(metric, row),
                direction=direction,
                tie_break_trace=(f"{metric}={row_value(metric, row)}", f"average_delay={row.average_delay}", f"deadline_violation_rate={row.deadline_violation_rate}", f"timeout_drop_rate={row.timeout_drop_rate}", f"policy={row.policy}"),
            )
            for index, row in enumerate(sorted_rows)
        )
        rankings[metric] = ranking_rows
    return rankings

