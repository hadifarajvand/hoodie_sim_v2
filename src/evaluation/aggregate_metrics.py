from __future__ import annotations

from .metrics import TraceMetrics, aggregate_terminal_rewards, evaluate_run


def compute_aggregate_metrics(trace_metrics: list[TraceMetrics]) -> dict[str, float | int]:
    return evaluate_run(trace_metrics)
