from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .config import (
    BLOCKED_STATUS,
    DEPENDENCY_FEATURES,
    EXPECTED_GROUPING_COUNTS,
    FEATURE_NAME,
    GROUPING_TYPES,
    READY_STATUS,
    REQUIRED_METRIC_NAMES,
    REQUIRED_POLICY_IDS,
    REQUIRED_SCENARIO_IDS,
    SUMMARY_FIELD_NAMES,
)


def _is_numeric(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_non_negative_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


@dataclass(frozen=True, slots=True)
class MetricSummary:
    metric_name: str
    mean: float
    std: float
    min: float
    max: float
    count: int
    ci95_low: float
    ci95_high: float

    def __post_init__(self) -> None:
        if self.metric_name not in REQUIRED_METRIC_NAMES:
            raise ValueError("metric_name must be one of the required metrics")
        if self.count <= 0:
            raise ValueError("count must be positive")
        for field_name in SUMMARY_FIELD_NAMES:
            if field_name == "count":
                continue
            if not _is_numeric(getattr(self, field_name)):
                raise ValueError(f"{field_name} must be numeric")
        if self.ci95_low > self.ci95_high:
            raise ValueError("ci95_low must not exceed ci95_high")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PolicyAggregate:
    policy_id: str
    policy_family: str
    row_count: int
    metric_summaries: tuple[MetricSummary, ...]

    def __post_init__(self) -> None:
        if self.policy_id not in REQUIRED_POLICY_IDS:
            raise ValueError("policy_id must be one of the required policies")
        if not self.policy_family:
            raise ValueError("policy_family must be non-empty")
        if self.row_count <= 0:
            raise ValueError("row_count must be positive")
        metric_names = [summary.metric_name for summary in self.metric_summaries]
        if len(metric_names) != len(set(metric_names)):
            raise ValueError("metric_summaries must not contain duplicates")
        if set(metric_names) != set(REQUIRED_METRIC_NAMES):
            raise ValueError("metric_summaries must cover every required metric")
        summary_counts = {summary.count for summary in self.metric_summaries}
        if len(summary_counts) != 1:
            raise ValueError("metric summaries must use the same sample count")
        if next(iter(summary_counts)) != self.row_count:
            raise ValueError("row_count must match the metric summary sample count")

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "policy_family": self.policy_family,
            "row_count": self.row_count,
            "metric_summaries": [summary.to_dict() for summary in self.metric_summaries],
        }


@dataclass(frozen=True, slots=True)
class ComparativeAggregate:
    grouping_type: str
    grouping_key: str
    row_count: int
    policy_aggregates: tuple[PolicyAggregate, ...]

    def __post_init__(self) -> None:
        if self.grouping_type not in GROUPING_TYPES:
            raise ValueError("grouping_type must be one of the required grouping types")
        if not self.grouping_key:
            raise ValueError("grouping_key must be non-empty")
        if self.row_count <= 0:
            raise ValueError("row_count must be positive")
        policy_ids = [aggregate.policy_id for aggregate in self.policy_aggregates]
        if len(policy_ids) != len(set(policy_ids)):
            raise ValueError("policy_aggregates must not contain duplicate policies")
        if self.grouping_type == "policy":
            if len(self.policy_aggregates) != 1:
                raise ValueError("policy grouping must contain exactly one policy aggregate")
        else:
            if set(policy_ids) != set(REQUIRED_POLICY_IDS):
                raise ValueError("comparative aggregates must represent all policies")
        if sum(aggregate.row_count for aggregate in self.policy_aggregates) != self.row_count:
            raise ValueError("row_count must equal the sum of policy aggregate row counts")

    def to_dict(self) -> dict[str, Any]:
        return {
            "grouping_type": self.grouping_type,
            "grouping_key": self.grouping_key,
            "row_count": self.row_count,
            "policy_aggregates": [aggregate.to_dict() for aggregate in self.policy_aggregates],
        }


@dataclass(frozen=True, slots=True)
class AggregationReport:
    feature_id: str
    status: str
    passed: bool
    dependency_features: tuple[str, ...]
    policy_aggregates: tuple[PolicyAggregate, ...]
    comparative_aggregates: tuple[ComparativeAggregate, ...]
    validation_summary: tuple[str, ...]
    claim_boundary: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.feature_id != "079-result-aggregation-statistical-summary":
            raise ValueError("feature_id must be 079-result-aggregation-statistical-summary")
        if self.status not in {READY_STATUS, BLOCKED_STATUS}:
            raise ValueError("status must be explicit and recognized")
        if tuple(self.dependency_features) != DEPENDENCY_FEATURES:
            raise ValueError("dependency_features must include Feature 078 and Feature 077")
        if not self.policy_aggregates:
            raise ValueError("policy_aggregates must be non-empty")
        if len(self.policy_aggregates) != len(REQUIRED_POLICY_IDS):
            raise ValueError("policy_aggregates must cover all required policies")
        policy_ids = [aggregate.policy_id for aggregate in self.policy_aggregates]
        if len(policy_ids) != len(set(policy_ids)):
            raise ValueError("policy_aggregates must not contain duplicate policies")
        if set(policy_ids) != set(REQUIRED_POLICY_IDS):
            raise ValueError("policy_aggregates must cover every required policy")
        if not self.comparative_aggregates:
            raise ValueError("comparative_aggregates must be non-empty")
        if not self.validation_summary:
            raise ValueError("validation_summary must be non-empty")
        if not self.claim_boundary:
            raise ValueError("claim_boundary must be non-empty")

        if not self._claim_boundary_is_explicit():
            raise ValueError("claim_boundary must contain the required claim boundary statements")

        if any(not aggregate.metric_summaries for aggregate in self.policy_aggregates):
            raise ValueError("policy aggregates must include metric summaries")
        if any(not aggregate.policy_aggregates for aggregate in self.comparative_aggregates):
            raise ValueError("comparative aggregates must include policy aggregates")

        expected_policy_groupings = EXPECTED_GROUPING_COUNTS["policy"]
        if sum(1 for aggregate in self.comparative_aggregates if aggregate.grouping_type == "policy") != expected_policy_groupings:
            raise ValueError("policy grouping coverage must include all required policies")
        if sum(1 for aggregate in self.comparative_aggregates if aggregate.grouping_type == "policy_scenario") != EXPECTED_GROUPING_COUNTS["policy_scenario"]:
            raise ValueError("policy_scenario grouping coverage must include all required scenarios")
        if sum(1 for aggregate in self.comparative_aggregates if aggregate.grouping_type == "policy_workload") != EXPECTED_GROUPING_COUNTS["policy_workload"]:
            raise ValueError("policy_workload grouping coverage must include all required workload levels")
        if sum(1 for aggregate in self.comparative_aggregates if aggregate.grouping_type == "policy_deadline") != EXPECTED_GROUPING_COUNTS["policy_deadline"]:
            raise ValueError("policy_deadline grouping coverage must include all required deadline levels")
        if sum(1 for aggregate in self.comparative_aggregates if aggregate.grouping_type == "policy_workload_deadline") != EXPECTED_GROUPING_COUNTS["policy_workload_deadline"]:
            raise ValueError("policy_workload_deadline grouping coverage must include all required workload/deadline combinations")

        if not all(summary.metric_name in REQUIRED_METRIC_NAMES for aggregate in self.policy_aggregates for summary in aggregate.metric_summaries):
            raise ValueError("policy aggregates must summarize every required metric")
        if not all(summary.ci95_low <= summary.mean <= summary.ci95_high for aggregate in self.policy_aggregates for summary in aggregate.metric_summaries):
            raise ValueError("policy aggregates must populate ci95 bounds")

        if self.passed and self.status != READY_STATUS:
            raise ValueError("passed reports must use the ready status")
        expected_pass = bool(
            all(aggregate.policy_id in REQUIRED_POLICY_IDS for aggregate in self.policy_aggregates)
            and all(summary.count > 0 for aggregate in self.policy_aggregates for summary in aggregate.metric_summaries)
            and all(summary.ci95_low <= summary.ci95_high for aggregate in self.policy_aggregates for summary in aggregate.metric_summaries)
            and all(comparative.grouping_type in GROUPING_TYPES for comparative in self.comparative_aggregates)
        )
        if self.passed != expected_pass:
            raise ValueError("passed must match the readiness gates")
        expected_status = READY_STATUS if expected_pass else BLOCKED_STATUS
        if self.status != expected_status:
            raise ValueError("status must match the computed readiness state")

    def _claim_boundary_is_explicit(self) -> bool:
        boundary = " ".join(self.claim_boundary).lower()
        required_phrases = (
            "no training claim",
            "no superiority claim",
            "no final evaluation claim",
            "no statistical significance claim",
            "no ranking claim",
            "no winner claim",
        )
        return all(phrase in boundary for phrase in required_phrases)

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "status": self.status,
            "passed": self.passed,
            "dependency_features": list(self.dependency_features),
            "policy_aggregates": [aggregate.to_dict() for aggregate in self.policy_aggregates],
            "comparative_aggregates": [aggregate.to_dict() for aggregate in self.comparative_aggregates],
            "validation_summary": list(self.validation_summary),
            "claim_boundary": list(self.claim_boundary),
        }
