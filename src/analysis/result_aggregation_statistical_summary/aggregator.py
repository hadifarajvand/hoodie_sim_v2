from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Sequence
from math import sqrt
from statistics import fmean, pstdev
from typing import Any

from src.analysis.campaign_execution_engine.model import CampaignExecutionResultRow

from .config import (
    EXPECTED_GROUPING_COUNTS,
    POLICY_FAMILY_BY_ID,
    REQUIRED_METRIC_NAMES,
    REQUIRED_POLICY_IDS,
    REQUIRED_SCENARIO_IDS,
    DEADLINE_PRESSURE_LEVELS,
    WORKLOAD_LEVELS,
)
from .model import ComparativeAggregate, MetricSummary, PolicyAggregate


def _metric_values(rows: Sequence[CampaignExecutionResultRow], metric_name: str) -> tuple[float, ...]:
    return tuple(float(getattr(row, metric_name)) for row in rows)


def _ci95_bounds(mean_value: float, std_value: float, count: int) -> tuple[float, float]:
    if count <= 1:
        return (mean_value, mean_value)
    margin = 1.96 * std_value / sqrt(count)
    return (mean_value - margin, mean_value + margin)


def summarize_metric(metric_name: str, values: Sequence[float]) -> MetricSummary:
    if metric_name not in REQUIRED_METRIC_NAMES:
        raise ValueError("metric_name must be one of the required metrics")
    if not values:
        raise ValueError("values must be non-empty")
    mean_value = float(fmean(values))
    std_value = float(pstdev(values)) if len(values) > 1 else 0.0
    min_value = float(min(values))
    max_value = float(max(values))
    ci95_low, ci95_high = _ci95_bounds(mean_value, std_value, len(values))
    return MetricSummary(
        metric_name=metric_name,
        mean=mean_value,
        std=std_value,
        min=min_value,
        max=max_value,
        count=len(values),
        ci95_low=float(ci95_low),
        ci95_high=float(ci95_high),
    )


def summarize_row_metrics(rows: Sequence[CampaignExecutionResultRow]) -> tuple[MetricSummary, ...]:
    if not rows:
        raise ValueError("rows must be non-empty")
    return tuple(summarize_metric(metric_name, _metric_values(rows, metric_name)) for metric_name in REQUIRED_METRIC_NAMES)


def _policy_rows(rows: Sequence[CampaignExecutionResultRow], policy_id: str) -> tuple[CampaignExecutionResultRow, ...]:
    return tuple(row for row in rows if row.policy_id == policy_id)


def build_policy_aggregate(rows: Sequence[CampaignExecutionResultRow], policy_id: str) -> PolicyAggregate:
    policy_rows = _policy_rows(rows, policy_id)
    if not policy_rows:
        raise ValueError(f"no rows found for policy {policy_id}")
    return PolicyAggregate(
        policy_id=policy_id,
        policy_family=POLICY_FAMILY_BY_ID[policy_id],
        row_count=len(policy_rows),
        metric_summaries=summarize_row_metrics(policy_rows),
    )


def build_policy_aggregates(rows: Sequence[CampaignExecutionResultRow]) -> tuple[PolicyAggregate, ...]:
    return tuple(build_policy_aggregate(rows, policy_id) for policy_id in REQUIRED_POLICY_IDS)


def _build_comparative_aggregate(
    *,
    grouping_type: str,
    grouping_key: str,
    rows: Sequence[CampaignExecutionResultRow],
    policy_filter: dict[str, Sequence[CampaignExecutionResultRow]] | None = None,
) -> ComparativeAggregate:
    if not rows:
        raise ValueError("comparative aggregate rows must be non-empty")
    if policy_filter is None:
        policy_filter = {policy_id: _policy_rows(rows, policy_id) for policy_id in REQUIRED_POLICY_IDS}
    policy_aggregates = tuple(
        PolicyAggregate(
            policy_id=policy_id,
            policy_family=POLICY_FAMILY_BY_ID[policy_id],
            row_count=len(policy_rows),
            metric_summaries=summarize_row_metrics(policy_rows),
        )
        for policy_id, policy_rows in policy_filter.items()
        if policy_rows
    )
    return ComparativeAggregate(
        grouping_type=grouping_type,
        grouping_key=grouping_key,
        row_count=len(rows),
        policy_aggregates=policy_aggregates,
    )


def build_comparative_aggregates(rows: Sequence[CampaignExecutionResultRow]) -> tuple[ComparativeAggregate, ...]:
    if not rows:
        raise ValueError("rows must be non-empty")
    comparative_aggregates: list[ComparativeAggregate] = []

    for policy_id in REQUIRED_POLICY_IDS:
        policy_rows = _policy_rows(rows, policy_id)
        comparative_aggregates.append(
            _build_comparative_aggregate(
                grouping_type="policy",
                grouping_key=f"policy={policy_id}",
                rows=policy_rows,
                policy_filter={policy_id: policy_rows},
            )
        )

    for scenario_id in REQUIRED_SCENARIO_IDS:
        scenario_rows = tuple(row for row in rows if row.scenario_id == scenario_id)
        comparative_aggregates.append(
            _build_comparative_aggregate(
                grouping_type="policy_scenario",
                grouping_key=f"scenario={scenario_id}",
                rows=scenario_rows,
            )
        )

    for workload_level in WORKLOAD_LEVELS:
        workload_rows = tuple(row for row in rows if row.workload_level == workload_level)
        comparative_aggregates.append(
            _build_comparative_aggregate(
                grouping_type="policy_workload",
                grouping_key=f"workload={workload_level}",
                rows=workload_rows,
            )
        )

    for deadline_pressure_level in DEADLINE_PRESSURE_LEVELS:
        deadline_rows = tuple(row for row in rows if row.deadline_pressure_level == deadline_pressure_level)
        comparative_aggregates.append(
            _build_comparative_aggregate(
                grouping_type="policy_deadline",
                grouping_key=f"deadline_pressure={deadline_pressure_level}",
                rows=deadline_rows,
            )
        )

    for workload_level in WORKLOAD_LEVELS:
        for deadline_pressure_level in DEADLINE_PRESSURE_LEVELS:
            combined_rows = tuple(
                row
                for row in rows
                if row.workload_level == workload_level and row.deadline_pressure_level == deadline_pressure_level
            )
            comparative_aggregates.append(
                _build_comparative_aggregate(
                    grouping_type="policy_workload_deadline",
                    grouping_key=f"workload={workload_level}|deadline_pressure={deadline_pressure_level}",
                    rows=combined_rows,
                )
            )

    expected_counts = EXPECTED_GROUPING_COUNTS
    observed_counts = {
        "policy": sum(1 for aggregate in comparative_aggregates if aggregate.grouping_type == "policy"),
        "policy_scenario": sum(1 for aggregate in comparative_aggregates if aggregate.grouping_type == "policy_scenario"),
        "policy_workload": sum(1 for aggregate in comparative_aggregates if aggregate.grouping_type == "policy_workload"),
        "policy_deadline": sum(1 for aggregate in comparative_aggregates if aggregate.grouping_type == "policy_deadline"),
        "policy_workload_deadline": sum(1 for aggregate in comparative_aggregates if aggregate.grouping_type == "policy_workload_deadline"),
    }
    if observed_counts != expected_counts:
        raise ValueError("comparative aggregate coverage is incomplete")
    return tuple(comparative_aggregates)


def verify_all_policies_and_metrics(
    policy_aggregates: Sequence[PolicyAggregate],
    comparative_aggregates: Sequence[ComparativeAggregate],
) -> None:
    policy_ids = {aggregate.policy_id for aggregate in policy_aggregates}
    if policy_ids != set(REQUIRED_POLICY_IDS):
        raise ValueError("all required policies must be represented")
    if any(set(summary.metric_name for summary in aggregate.metric_summaries) != set(REQUIRED_METRIC_NAMES) for aggregate in policy_aggregates):
        raise ValueError("all required metrics must be represented")
    if any(summary.count <= 0 for aggregate in policy_aggregates for summary in aggregate.metric_summaries):
        raise ValueError("metric summaries must have positive sample counts")
    if any(summary.ci95_low is None or summary.ci95_high is None for aggregate in policy_aggregates for summary in aggregate.metric_summaries):
        raise ValueError("ci95 fields must be populated")
    if not comparative_aggregates:
        raise ValueError("comparative aggregates must be non-empty")
