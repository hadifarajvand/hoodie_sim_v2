from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .config import ACTIVE_POLICIES, ALLOWED_PAPER_COMPARISON_METRICS, INVALID_LABELS, REQUIRED_METRICS, VERDICTS


ALLOWED_EXTRACTION_METHODS = ("explicit_text", "table_value", "figure_digitized", "qualitative_only", "unavailable")
ALLOWED_CONFIDENCE = ("high", "medium", "low")
ALLOWED_MAPPING_STATUS = ("exact_metric_match", "derived_metric_match", "approximate_metric_match", "not_available_in_simulator", "not_reported_by_paper")
ALLOWED_COMPARISON_STATUS = ("aligned", "partially_aligned", "divergent", "not_comparable")


def _non_empty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


@dataclass(frozen=True, slots=True)
class PaperOutputItem:
    paper_item_id: str
    source_location: str
    item_type: str
    metric: str
    policies: tuple[str, ...]
    scenario_variable: str
    paper_values: Any
    value_extraction_method: str
    extraction_confidence: str
    notes: str

    def __post_init__(self) -> None:
        if not _non_empty(self.paper_item_id):
            raise ValueError("paper_item_id must be non-empty")
        if not _non_empty(self.source_location):
            raise ValueError("source_location must be non-empty")
        if not _non_empty(self.item_type):
            raise ValueError("item_type must be non-empty")
        if self.metric not in REQUIRED_METRICS and self.metric != "none":
            raise ValueError(f"unknown metric: {self.metric}")
        if self.value_extraction_method not in ALLOWED_EXTRACTION_METHODS:
            raise ValueError("invalid value_extraction_method")
        if self.extraction_confidence not in ALLOWED_CONFIDENCE:
            raise ValueError("invalid extraction_confidence")
        if not _non_empty(self.notes):
            raise ValueError("notes must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["policies"] = list(self.policies)
        return payload


@dataclass(frozen=True, slots=True)
class SimulatorOutputItem:
    artifact_path: str
    metric: str
    policy: str
    scenario: str
    value: float | int | None
    aggregation_method: str
    source_feature: str
    claim_boundary: str

    def __post_init__(self) -> None:
        if not _non_empty(self.artifact_path):
            raise ValueError("artifact_path must be non-empty")
        if self.metric not in REQUIRED_METRICS:
            raise ValueError(f"unknown metric: {self.metric}")
        if self.policy not in ACTIVE_POLICIES:
            raise ValueError(f"unknown policy: {self.policy}")
        if not _non_empty(self.scenario):
            raise ValueError("scenario must be non-empty")
        if not _non_empty(self.aggregation_method):
            raise ValueError("aggregation_method must be non-empty")
        if self.source_feature not in {"085", "086", "087"}:
            raise ValueError("source_feature must be one of 085/086/087")
        if not _non_empty(self.claim_boundary):
            raise ValueError("claim_boundary must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class MetricAlignmentRow:
    paper_metric: str
    simulator_metric: str
    classification: str
    mapping_status: str
    allowed_for_comparison: bool
    caveat: str

    def __post_init__(self) -> None:
        if self.paper_metric not in REQUIRED_METRICS:
            raise ValueError(f"unknown paper_metric: {self.paper_metric}")
        if self.simulator_metric not in REQUIRED_METRICS:
            raise ValueError(f"unknown simulator_metric: {self.simulator_metric}")
        if self.classification not in {
            "paper_primary_metric",
            "paper_secondary_or_derived_metric",
            "paper_secondary_or_repository_metric",
            "repository_diagnostic_metric",
            "not_for_paper_comparison",
        }:
            raise ValueError("invalid classification")
        if self.mapping_status not in ALLOWED_MAPPING_STATUS:
            raise ValueError("invalid mapping_status")
        if not _non_empty(self.caveat):
            raise ValueError("caveat must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class OutputComparisonRow:
    paper_item_id: str
    metric: str
    policy: str
    scenario_or_x_axis: str
    paper_value: Any
    simulator_value: float | int | None
    absolute_difference: float | None
    relative_difference: float | None
    ranking_match: bool | None
    qualitative_agreement: str
    comparison_status: str
    notes: str

    def __post_init__(self) -> None:
        if not _non_empty(self.paper_item_id):
            raise ValueError("paper_item_id must be non-empty")
        if self.metric not in REQUIRED_METRICS:
            raise ValueError(f"unknown metric: {self.metric}")
        if self.policy not in ACTIVE_POLICIES:
            raise ValueError(f"unknown policy: {self.policy}")
        if not _non_empty(self.scenario_or_x_axis):
            raise ValueError("scenario_or_x_axis must be non-empty")
        if self.qualitative_agreement not in ALLOWED_COMPARISON_STATUS:
            raise ValueError("invalid qualitative_agreement")
        if self.comparison_status not in ALLOWED_COMPARISON_STATUS:
            raise ValueError("invalid comparison_status")
        if not _non_empty(self.notes):
            raise ValueError("notes must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class FigureComparisonCoverageRow:
    figure_id: str
    paper_item_ids: tuple[str, ...]
    comparison_status: str
    notes: str

    def __post_init__(self) -> None:
        if not _non_empty(self.figure_id):
            raise ValueError("figure_id must be non-empty")
        if not self.paper_item_ids:
            raise ValueError("paper_item_ids must be non-empty")
        if self.comparison_status not in ALLOWED_COMPARISON_STATUS:
            raise ValueError("invalid comparison_status")
        if not _non_empty(self.notes):
            raise ValueError("notes must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["paper_item_ids"] = list(self.paper_item_ids)
        return payload


@dataclass(frozen=True, slots=True)
class RankingAgreementRow:
    metric: str
    simulator_ranking: tuple[str, ...]
    paper_ranking: tuple[str, ...] | None
    agreement_level: str
    notes: str

    def __post_init__(self) -> None:
        if self.metric not in ALLOWED_PAPER_COMPARISON_METRICS:
            raise ValueError(f"unknown metric: {self.metric}")
        if not self.simulator_ranking:
            raise ValueError("simulator_ranking must be non-empty")
        if self.agreement_level not in {"exact", "partial", "not_available"}:
            raise ValueError("invalid agreement_level")
        if not _non_empty(self.notes):
            raise ValueError("notes must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["simulator_ranking"] = list(self.simulator_ranking)
        payload["paper_ranking"] = None if self.paper_ranking is None else list(self.paper_ranking)
        return payload


@dataclass(frozen=True, slots=True)
class ComparisonReport:
    feature_id: str
    verdict: str
    feature_086_boundary: tuple[str, ...]
    paper_items_extracted: int
    paper_items_comparable: int
    paper_items_not_comparable: int
    allowed_metrics: tuple[str, ...]
    diagnostic_metrics: tuple[str, ...]
    ranking_agreement_summary: dict[str, Any]
    numeric_difference_summary: dict[str, Any]
    blocking_issues: tuple[str, ...]
    remaining_limitations: tuple[str, ...]
    comparable_paper_outputs: tuple[str, ...]
    non_comparable_paper_outputs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.verdict not in VERDICTS:
            raise ValueError("invalid verdict")
        if not self.feature_086_boundary:
            raise ValueError("feature_086_boundary must be non-empty")
        if not self.allowed_metrics:
            raise ValueError("allowed_metrics must be non-empty")
        if not self.diagnostic_metrics:
            raise ValueError("diagnostic_metrics must be non-empty")
        if not self.remaining_limitations:
            raise ValueError("remaining_limitations must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "verdict": self.verdict,
            "feature_086_boundary": list(self.feature_086_boundary),
            "paper_items_extracted": self.paper_items_extracted,
            "paper_items_comparable": self.paper_items_comparable,
            "paper_items_not_comparable": self.paper_items_not_comparable,
            "allowed_metrics": list(self.allowed_metrics),
            "diagnostic_metrics": list(self.diagnostic_metrics),
            "ranking_agreement_summary": self.ranking_agreement_summary,
            "numeric_difference_summary": self.numeric_difference_summary,
            "blocking_issues": list(self.blocking_issues),
            "remaining_limitations": list(self.remaining_limitations),
            "comparable_paper_outputs": list(self.comparable_paper_outputs),
            "non_comparable_paper_outputs": list(self.non_comparable_paper_outputs),
        }
