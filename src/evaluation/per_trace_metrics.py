from __future__ import annotations

from .metrics import TaskEvaluationRecord, TraceMetrics, evaluate_trace


def compute_per_trace_metrics(
    *,
    trace_id: str,
    policy_name: str,
    seed: int,
    device: str,
    records: list[TaskEvaluationRecord],
) -> TraceMetrics:
    return evaluate_trace(
        trace_id=trace_id,
        policy_name=policy_name,
        seed=seed,
        device=device,
        records=records,
    )
