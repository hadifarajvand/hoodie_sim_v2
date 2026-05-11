from __future__ import annotations

from enum import Enum


class ComparisonClassification(str, Enum):
    MATCH = "match"
    DIVERGENCE = "divergence"
    ASSUMPTION_GAP = "assumption_gap"
    UNSUPPORTED_BY_ENVIRONMENT_TRACE = "unsupported_by_environment_trace"
    BLOCKED_BY_RUNTIME_TOPOLOGY_OR_DESTINATION_FIXTURE = "blocked_by_runtime_topology_or_destination_fixture"
    UNSUPPORTED_BY_REFERENCE_KERNEL = "unsupported_by_reference_kernel"
    INCONCLUSIVE = "inconclusive"


class FindingCause(str, Enum):
    LIKELY_ENVIRONMENT_BUG = "likely_environment_bug"
    LIKELY_REFERENCE_GAP = "likely_reference_gap"
    PAPER_ASSUMPTION_GAP = "paper_assumption_gap"
    INSTRUMENTATION_GAP = "instrumentation_gap"
    EXPECTED_SCOPE_DIFFERENCE = "expected_scope_difference"
    UNRESOLVED = "unresolved"


def classify_comparison(
    *,
    reference_summary: dict[str, object],
    environment_summary: dict[str, object],
    environment_supported: bool,
    reference_supported: bool = True,
    environment_blocked_reason: str | None = None,
) -> tuple[ComparisonClassification, FindingCause]:
    if not reference_supported:
        return ComparisonClassification.UNSUPPORTED_BY_REFERENCE_KERNEL, FindingCause.LIKELY_REFERENCE_GAP
    if not environment_supported:
        if environment_blocked_reason == "runtime_topology_or_destination_fixture":
            return (
                ComparisonClassification.BLOCKED_BY_RUNTIME_TOPOLOGY_OR_DESTINATION_FIXTURE,
                FindingCause.EXPECTED_SCOPE_DIFFERENCE,
            )
        return ComparisonClassification.UNSUPPORTED_BY_ENVIRONMENT_TRACE, FindingCause.INSTRUMENTATION_GAP

    reference_events = tuple(reference_summary.get("event_sequence", ()))
    environment_events = tuple(environment_summary.get("event_sequence", ()))
    if not reference_events or not environment_events:
        return ComparisonClassification.INCONCLUSIVE, FindingCause.UNRESOLVED
    if reference_events == environment_events:
        return ComparisonClassification.MATCH, FindingCause.EXPECTED_SCOPE_DIFFERENCE

    reference_terminal = reference_summary.get("terminal_status")
    environment_terminal = environment_summary.get("terminal_status")
    if reference_terminal != environment_terminal:
        return ComparisonClassification.DIVERGENCE, FindingCause.LIKELY_ENVIRONMENT_BUG
    if reference_summary.get("reward_timing") != environment_summary.get("reward_timing"):
        return ComparisonClassification.DIVERGENCE, FindingCause.PAPER_ASSUMPTION_GAP
    return ComparisonClassification.ASSUMPTION_GAP, FindingCause.PAPER_ASSUMPTION_GAP
