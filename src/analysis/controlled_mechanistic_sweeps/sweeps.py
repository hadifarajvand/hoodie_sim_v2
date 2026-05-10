from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _jsonable_value(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_jsonable_value(item) for item in value]
    if isinstance(value, list):
        return [_jsonable_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable_value(item) for key, item in value.items()}
    return value


@dataclass(slots=True)
class SweepDefinition:
    name: str
    parameter: str
    values: tuple[Any, ...]
    fixed_seeds: tuple[int, ...]
    expected_direction: str
    control_source: str
    control_available: bool = True
    control_notes: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "parameter": self.parameter,
            "values": [_jsonable_value(value) for value in self.values],
            "fixed_seeds": list(self.fixed_seeds),
            "expected_direction": self.expected_direction,
            "control_source": self.control_source,
            "control_available": self.control_available,
            "control_notes": self.control_notes,
        }


@dataclass(slots=True)
class FixedInput:
    sweep_name: str
    seed: int
    parameter_value: Any
    trace_identifier: str
    control_notes: str

    def to_dict(self) -> dict[str, object]:
        return {
            "sweep_name": self.sweep_name,
            "seed": self.seed,
            "parameter_value": _jsonable_value(self.parameter_value),
            "trace_identifier": self.trace_identifier,
            "control_notes": self.control_notes,
        }


@dataclass(slots=True)
class SweepObservation:
    sweep_name: str
    seed: int
    parameter_value: Any
    observed_pressure_indicator: float | None
    observed_outcome_summary: str
    evidence_available: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "sweep_name": self.sweep_name,
            "seed": self.seed,
            "parameter_value": _jsonable_value(self.parameter_value),
            "observed_pressure_indicator": self.observed_pressure_indicator,
            "observed_outcome_summary": self.observed_outcome_summary,
            "evidence_available": self.evidence_available,
        }


@dataclass(slots=True)
class MonotonicCheck:
    sweep_name: str
    status: str
    support_level: str
    rationale: str

    def to_dict(self) -> dict[str, object]:
        return {
            "sweep_name": self.sweep_name,
            "status": self.status,
            "support_level": self.support_level,
            "rationale": self.rationale,
        }


@dataclass(slots=True)
class ControlledMechanisticSweepReport:
    metadata: dict[str, Any]
    sweep_definitions: list[SweepDefinition] = field(default_factory=list)
    fixed_inputs: list[FixedInput] = field(default_factory=list)
    observations: list[SweepObservation] = field(default_factory=list)
    monotonic_checks: list[MonotonicCheck] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    instrumentation_gaps: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    no_campaign_rerun_disclaimer: str = ""
    no_paper_validity_disclaimer: str = ""
    reproducibility: dict[str, Any] = field(default_factory=dict)
    overall_status: str = "pass"

    def to_dict(self) -> dict[str, object]:
        return {
            "metadata": dict(self.metadata),
            "sweep_definitions": [definition.to_dict() for definition in self.sweep_definitions],
            "fixed_inputs": [fixed_input.to_dict() for fixed_input in self.fixed_inputs],
            "observations": [observation.to_dict() for observation in self.observations],
            "monotonic_checks": [check.to_dict() for check in self.monotonic_checks],
            "warnings": list(self.warnings),
            "instrumentation_gaps": list(self.instrumentation_gaps),
            "limitations": list(self.limitations),
            "no_campaign_rerun_disclaimer": self.no_campaign_rerun_disclaimer,
            "no_paper_validity_disclaimer": self.no_paper_validity_disclaimer,
            "reproducibility": dict(self.reproducibility),
            "overall_status": self.overall_status,
        }


def build_controlled_mechanistic_sweep_definitions() -> tuple[SweepDefinition, ...]:
    fixed_seeds = (7,)
    return (
        SweepDefinition(
            name="arrival_probability",
            parameter="arrival_probability",
            values=(0.2, 0.5, 0.8),
            fixed_seeds=fixed_seeds,
            expected_direction="nondecreasing",
            control_source="TrafficConfig.arrival_probability",
            control_available=True,
            control_notes="Controlled through the public traffic configuration.",
        ),
        SweepDefinition(
            name="timeout",
            parameter="timeout_slots",
            values=(1, 2, 3),
            fixed_seeds=fixed_seeds,
            expected_direction="nonincreasing",
            control_source="TrafficConfig.timeout_slots",
            control_available=True,
            control_notes="Controlled through the public traffic configuration.",
        ),
        SweepDefinition(
            name="cpu_capacity",
            parameter="cpu_capacity_per_slot_agent",
            values=(1.0, 2.0, 4.0),
            fixed_seeds=fixed_seeds,
            expected_direction="nondecreasing",
            control_source="ComputeConfig.cpu_capacity_per_slot_agent",
            control_available=True,
            control_notes="Controlled through the public compute configuration.",
        ),
        SweepDefinition(
            name="link_rate",
            parameter="link_rate",
            values=("low", "medium", "high"),
            fixed_seeds=fixed_seeds,
            expected_direction="nondecreasing",
            control_source="unsupported",
            control_available=False,
            control_notes="No direct public link-rate hook exists in the current environment interface.",
        ),
        SweepDefinition(
            name="topology_density",
            parameter="topology_density",
            values=("sparse", "default", "dense"),
            fixed_seeds=fixed_seeds,
            expected_direction="nondecreasing",
            control_source="TopologyGraph.legal_adjacency",
            control_available=True,
            control_notes="Controlled through the public topology interface.",
        ),
    )
