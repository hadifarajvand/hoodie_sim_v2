from __future__ import annotations

from collections.abc import Iterable

from .sweeps import MonotonicCheck, SweepDefinition, SweepObservation


def _directional_deltas(values: list[float]) -> list[float]:
    return [right - left for left, right in zip(values, values[1:])]


def classify_monotonic(definition: SweepDefinition, observations: Iterable[SweepObservation]) -> MonotonicCheck:
    obs_list = list(observations)
    if not definition.control_available:
        return MonotonicCheck(
            sweep_name=definition.name,
            status="instrumentation_gap",
            support_level="none",
            rationale=f"{definition.name} has no direct public control source: {definition.control_source}.",
        )
    if not obs_list or any(not observation.evidence_available for observation in obs_list):
        return MonotonicCheck(
            sweep_name=definition.name,
            status="instrumentation_gap",
            support_level="none",
            rationale=f"{definition.name} lacks sufficient public evidence to establish qualitative direction.",
        )

    numeric_values = [float(observation.observed_pressure_indicator) for observation in obs_list if observation.observed_pressure_indicator is not None]
    if len(numeric_values) < 2:
        return MonotonicCheck(
            sweep_name=definition.name,
            status="inconclusive",
            support_level="partial",
            rationale=f"{definition.name} produced too few measurable observations for a directional check.",
        )

    deltas = _directional_deltas(numeric_values)
    if definition.expected_direction == "nondecreasing":
        if any(delta < 0 for delta in deltas):
            return MonotonicCheck(
                sweep_name=definition.name,
                status="inconclusive",
                support_level="mixed",
                rationale=f"{definition.name} decreased at least once: {numeric_values}.",
            )
        if all(delta == 0 for delta in deltas):
            return MonotonicCheck(
                sweep_name=definition.name,
                status="warn",
                support_level="partial",
                rationale=f"{definition.name} remained flat across the tiny sweep: {numeric_values}.",
            )
        return MonotonicCheck(
            sweep_name=definition.name,
            status="pass",
            support_level="full",
            rationale=f"{definition.name} rose monotonically: {numeric_values}.",
        )
    if definition.expected_direction == "nonincreasing":
        if any(delta > 0 for delta in deltas):
            return MonotonicCheck(
                sweep_name=definition.name,
                status="inconclusive",
                support_level="mixed",
                rationale=f"{definition.name} increased at least once: {numeric_values}.",
            )
        if all(delta == 0 for delta in deltas):
            return MonotonicCheck(
                sweep_name=definition.name,
                status="warn",
                support_level="partial",
                rationale=f"{definition.name} remained flat across the tiny sweep: {numeric_values}.",
            )
        return MonotonicCheck(
            sweep_name=definition.name,
            status="pass",
            support_level="full",
            rationale=f"{definition.name} fell monotonically: {numeric_values}.",
        )
    return MonotonicCheck(
        sweep_name=definition.name,
        status="inconclusive",
        support_level="none",
        rationale=f"{definition.name} uses an unsupported expected direction: {definition.expected_direction}.",
    )
