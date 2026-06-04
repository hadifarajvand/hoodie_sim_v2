from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .config import ALLOWED_OUTPUT_STATUS, ALLOWED_PRIORITY


def _non_empty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


@dataclass(frozen=True, slots=True)
class PaperFigure:
    figure_id: str
    family: str
    paper_section: str
    caption: str
    metric: str
    x_axis: str
    sweep_values: tuple[Any, ...]
    policies_or_curves: tuple[str, ...]
    scenario_setup: str
    requires_training: bool
    requires_lstm: bool
    requires_digitization: bool
    priority: str
    output_status: str
    extraction_confidence: str
    pdf_verified: bool
    ocr_caveat: str
    simulator_output_requirement_id: str | None
    claim_boundary: tuple[str, ...]

    def __post_init__(self) -> None:
        if not _non_empty(self.figure_id):
            raise ValueError("figure_id must be non-empty")
        if self.priority not in ALLOWED_PRIORITY:
            raise ValueError("invalid priority")
        if self.output_status not in ALLOWED_OUTPUT_STATUS:
            raise ValueError("invalid output_status")
        if not _non_empty(self.paper_section):
            raise ValueError("paper_section must be non-empty")
        if not _non_empty(self.caption):
            raise ValueError("caption must be non-empty")
        if not _non_empty(self.metric):
            raise ValueError("metric must be non-empty")
        if not _non_empty(self.x_axis):
            raise ValueError("x_axis must be non-empty")
        if not _non_empty(self.scenario_setup):
            raise ValueError("scenario_setup must be non-empty")
        if not self.claim_boundary:
            raise ValueError("claim_boundary must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["sweep_values"] = list(self.sweep_values)
        payload["policies_or_curves"] = list(self.policies_or_curves)
        payload["claim_boundary"] = list(self.claim_boundary)
        return payload


@dataclass(frozen=True, slots=True)
class PaperMetric:
    metric_id: str
    paper_names: tuple[str, ...]
    definition: str
    used_in_figures: tuple[str, ...]
    primary_or_secondary: str
    simulator_metric_mapping: str | None
    requires_training: bool
    requires_lstm: bool
    comparison_allowed_now: bool
    claim_boundary: tuple[str, ...]

    def __post_init__(self) -> None:
        if not _non_empty(self.metric_id):
            raise ValueError("metric_id must be non-empty")
        if not self.paper_names:
            raise ValueError("paper_names must be non-empty")
        if not _non_empty(self.definition):
            raise ValueError("definition must be non-empty")
        if not self.used_in_figures:
            raise ValueError("used_in_figures must be non-empty")
        if not _non_empty(self.primary_or_secondary):
            raise ValueError("primary_or_secondary must be non-empty")
        if not self.claim_boundary:
            raise ValueError("claim_boundary must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["paper_names"] = list(self.paper_names)
        payload["used_in_figures"] = list(self.used_in_figures)
        payload["claim_boundary"] = list(self.claim_boundary)
        return payload


@dataclass(frozen=True, slots=True)
class SimulatorOutputRequirement:
    requirement_id: str
    target_figures: tuple[str, ...]
    output_family: str
    metrics: tuple[str, ...]
    policies: tuple[str, ...]
    x_axis: str
    sweep_values: tuple[Any, ...]
    scenario_setup: str
    artifact_outputs: tuple[str, ...]
    implementation_priority: str
    blocked_by_training: bool
    blocked_by_lstm: bool
    blocked_by_simulator_support: bool
    notes: str
    claim_boundary: tuple[str, ...]

    def __post_init__(self) -> None:
        if not _non_empty(self.requirement_id):
            raise ValueError("requirement_id must be non-empty")
        if not self.target_figures:
            raise ValueError("target_figures must be non-empty")
        if not _non_empty(self.output_family):
            raise ValueError("output_family must be non-empty")
        if not self.metrics:
            raise ValueError("metrics must be non-empty")
        if not self.policies:
            raise ValueError("policies must be non-empty")
        if not _non_empty(self.x_axis):
            raise ValueError("x_axis must be non-empty")
        if not self.sweep_values:
            raise ValueError("sweep_values must be non-empty")
        if not _non_empty(self.scenario_setup):
            raise ValueError("scenario_setup must be non-empty")
        if not self.artifact_outputs:
            raise ValueError("artifact_outputs must be non-empty")
        if not _non_empty(self.implementation_priority):
            raise ValueError("implementation_priority must be non-empty")
        if not _non_empty(self.notes):
            raise ValueError("notes must be non-empty")
        if not self.claim_boundary:
            raise ValueError("claim_boundary must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["target_figures"] = list(self.target_figures)
        payload["metrics"] = list(self.metrics)
        payload["policies"] = list(self.policies)
        payload["sweep_values"] = list(self.sweep_values)
        payload["artifact_outputs"] = list(self.artifact_outputs)
        payload["claim_boundary"] = list(self.claim_boundary)
        return payload


@dataclass(frozen=True, slots=True)
class Feature089Report:
    feature_id: str
    verdict: str
    source_truth_files: tuple[str, ...]
    figures_cataloged: int
    metrics_cataloged: int
    simulator_output_requirements: int
    priority_1_figures: tuple[str, ...]
    priority_2_figures: tuple[str, ...]
    priority_3_figures: tuple[str, ...]
    ready_now_figures: tuple[str, ...]
    future_required_figures: tuple[str, ...]
    blocked_figures: tuple[str, ...]
    feature_086_boundary: tuple[str, ...]
    feature_080_boundary: tuple[str, ...]
    allowed_policies: tuple[str, ...]
    remaining_limitations: tuple[str, ...]

    def __post_init__(self) -> None:
        if not _non_empty(self.feature_id):
            raise ValueError("feature_id must be non-empty")
        if not _non_empty(self.verdict):
            raise ValueError("verdict must be non-empty")
        if not self.source_truth_files:
            raise ValueError("source_truth_files must be non-empty")
        if self.figures_cataloged <= 0:
            raise ValueError("figures_cataloged must be positive")
        if self.metrics_cataloged <= 0:
            raise ValueError("metrics_cataloged must be positive")
        if self.simulator_output_requirements <= 0:
            raise ValueError("simulator_output_requirements must be positive")
        if not self.allowed_policies:
            raise ValueError("allowed_policies must be non-empty")
        if not self.feature_086_boundary or not self.feature_080_boundary:
            raise ValueError("claim boundaries must be non-empty")
        if not self.remaining_limitations:
            raise ValueError("remaining_limitations must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_id": self.feature_id,
            "verdict": self.verdict,
            "source_truth_files": list(self.source_truth_files),
            "figures_cataloged": self.figures_cataloged,
            "metrics_cataloged": self.metrics_cataloged,
            "simulator_output_requirements": self.simulator_output_requirements,
            "priority_1_figures": list(self.priority_1_figures),
            "priority_2_figures": list(self.priority_2_figures),
            "priority_3_figures": list(self.priority_3_figures),
            "ready_now_figures": list(self.ready_now_figures),
            "future_required_figures": list(self.future_required_figures),
            "blocked_figures": list(self.blocked_figures),
            "feature_086_boundary": list(self.feature_086_boundary),
            "feature_080_boundary": list(self.feature_080_boundary),
            "allowed_policies": list(self.allowed_policies),
            "remaining_limitations": list(self.remaining_limitations),
        }

