from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from collections.abc import Mapping, Sequence

from .common import (
    action_family,
    fallback_action,
    first_legal_family_action,
    legal_actions,
    observation_mapping,
)
from .policy_interface import PolicyContext, SharedPolicy


@dataclass(frozen=True, slots=True)
class DelayCandidate:
    action_family: str
    action_id: str
    available: bool
    queue_delay: float | None = None
    transmission_delay: float | None = None
    compute_delay: float | None = None
    total_delay: float | None = None
    tie_break_key: tuple[int, int, str] = (0, 0, "")
    fallback_notes: str | None = None


_LEGACY_FAMILY_TIE_ORDER = {"local": 0, "horizontal": 1, "vertical": 2}
_PLACEMENT_TIE_ORDER = {"local": 0, "vertical": 1, "horizontal": 2}


class MinimumLatencyEstimateOffloadingPolicy(SharedPolicy):
    def __init__(self) -> None:
        self.last_candidates: tuple[DelayCandidate, ...] = ()
        self.last_fallback_reason: str | None = None

    def choose_action(self, context: PolicyContext) -> str:
        self.last_fallback_reason = None
        candidates = build_delay_candidates(context)
        self.last_candidates = candidates
        comparable = [candidate for candidate in candidates if candidate.available and candidate.total_delay is not None]
        if comparable:
            comparable.sort(key=lambda candidate: (candidate.total_delay, candidate.tie_break_key))
            return comparable[0].action_id

        self.last_fallback_reason = _fallback_reason(candidates)
        fallback_from_hints = _fallback_from_hints(context)
        if fallback_from_hints is not None:
            return fallback_from_hints
        return fallback_action(context)


def build_delay_candidates(context: PolicyContext) -> tuple[DelayCandidate, ...]:
    observation = observation_mapping(context)
    legal = set(legal_actions(context))
    placement_candidates = _build_placement_delay_candidates(context, observation, legal)
    if placement_candidates:
        return tuple(placement_candidates)
    return _build_legacy_delay_candidates(context, observation, legal)


def _build_legacy_delay_candidates(
    context: PolicyContext,
    observation: Mapping[str, object],
    legal: set[str],
) -> list[DelayCandidate]:
    candidates: list[DelayCandidate] = []
    for family in ("local", "horizontal", "vertical"):
        action_id = _candidate_action_id(context, observation, family, legal)
        queue = _delay_component(observation, family, "queue_delay")
        transmission = _delay_component(observation, family, "transmission_delay")
        compute = _delay_component(observation, family, "compute_delay")
        total = _total_delay(observation, family, queue, transmission, compute)
        notes = None if total is not None else "missing comparable delay estimate"
        candidates.append(
            DelayCandidate(
                action_family=family,
                action_id=action_id,
                available=action_id in legal,
                queue_delay=queue,
                transmission_delay=transmission,
                compute_delay=compute,
                total_delay=total,
                tie_break_key=(_LEGACY_FAMILY_TIE_ORDER[family], 0, action_id),
                fallback_notes=notes,
            )
        )
    return candidates


def _build_placement_delay_candidates(
    context: PolicyContext,
    observation: Mapping[str, object],
    legal: set[str],
) -> list[DelayCandidate]:
    raw_candidates = observation.get("mleo_placement_candidates")
    if raw_candidates is None:
        return []
    candidates: list[DelayCandidate] = []
    for index, (default_key, candidate_payload) in enumerate(_iter_placement_candidate_payloads(raw_candidates)):
        candidate = _placement_delay_candidate(context, observation, legal, candidate_payload, default_key, index)
        if candidate is not None:
            candidates.append(candidate)
    return candidates


def _iter_placement_candidate_payloads(value: object) -> tuple[tuple[str | None, object], ...]:
    entries: list[tuple[str | None, object]] = []
    if isinstance(value, Mapping):
        for key, payload in value.items():
            entries.append((str(key), payload))
        return tuple(entries)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for payload in value:
            entries.append((None, payload))
    return tuple(entries)


def _placement_delay_candidate(
    context: PolicyContext,
    observation: Mapping[str, object],
    legal: set[str],
    payload: object,
    default_key: str | None,
    index: int,
) -> DelayCandidate | None:
    if not isinstance(payload, Mapping):
        return None

    action_id = _string_value(
        payload.get("action_id")
        or payload.get("action")
        or payload.get("destination_id")
        or payload.get("destination")
        or payload.get("placement_id")
        or default_key
    )
    if action_id is None:
        return None

    family = _string_value(payload.get("action_family") or payload.get("family") or payload.get("placement_kind"))
    if family is None:
        family = _infer_family_from_action_id(action_id, default_key)

    queue = _candidate_delay_value(observation, payload, action_id, family, "queue_delay")
    transmission = _candidate_delay_value(observation, payload, action_id, family, "transmission_delay")
    compute = _candidate_delay_value(observation, payload, action_id, family, "compute_delay")
    total = _candidate_total_delay(observation, payload, action_id, family, queue, transmission, compute)
    available = (action_id in legal) and bool(payload.get("available", True))
    source_agent_id = _string_value(observation.get("source_agent_id"))
    if family == "horizontal" and source_agent_id is not None and action_id == source_agent_id:
        available = False
    notes = None if total is not None else "missing comparable delay estimate"
    return DelayCandidate(
        action_family=family,
        action_id=action_id,
        available=available,
        queue_delay=queue,
        transmission_delay=transmission,
        compute_delay=compute,
        total_delay=total,
        tie_break_key=(_PLACEMENT_TIE_ORDER.get(family, len(_PLACEMENT_TIE_ORDER)), index, action_id),
        fallback_notes=notes,
    )


def _candidate_action_id(context: PolicyContext, observation: Mapping[str, object], family: str, legal: set[str]) -> str:
    candidate_payload = _candidate_payload(observation, family)
    if isinstance(candidate_payload, Mapping):
        action_id = candidate_payload.get("action_id")
        if isinstance(action_id, str) and action_id:
            return action_id
    preferred = first_legal_family_action(context, family)
    if preferred is not None:
        return preferred
    fallback = {"local": "local", "horizontal": "horizontal", "vertical": "vertical"}[family]
    return fallback if fallback in legal else fallback


def _candidate_payload(observation: Mapping[str, object], family: str) -> object:
    for key in ("mleo_delay_candidates", "delay_candidates"):
        payload = observation.get(key)
        if isinstance(payload, Mapping) and family in payload:
            return payload[family]
    return None


def _delay_component(observation: Mapping[str, object], family: str, component: str) -> float | None:
    candidate_payload = _candidate_payload(observation, family)
    if isinstance(candidate_payload, Mapping):
        value = candidate_payload.get(component)
        numeric = _numeric(value)
        if numeric is not None:
            return numeric
    value = observation.get(f"{family}_{component}")
    return _numeric(value)


def _total_delay(
    observation: Mapping[str, object],
    family: str,
    queue_delay: float | None,
    transmission_delay: float | None,
    compute_delay: float | None,
) -> float | None:
    candidate_payload = _candidate_payload(observation, family)
    if isinstance(candidate_payload, Mapping):
        explicit = _numeric(candidate_payload.get("total_delay"))
        if explicit is not None:
            return explicit
    latency_estimates = observation.get("latency_estimates")
    if isinstance(latency_estimates, Mapping):
        estimate = _numeric(latency_estimates.get(family))
        if estimate is not None:
            return estimate
    explicit = _numeric(observation.get(f"{family}_total_delay"))
    if explicit is not None:
        return explicit
    propagation = _numeric(observation.get(f"{family}_propagation_delay") or observation.get("propagation_delay"))
    load = _numeric(observation.get(f"{family}_destination_load") or observation.get("destination_load"))
    components = [component for component in (queue_delay, transmission_delay, propagation, compute_delay, load) if component is not None]
    if components:
        return float(sum(components))
    return None


def _numeric(value: object) -> float | None:
    if isinstance(value, (int, float)):
        numeric = float(value)
        if isfinite(numeric):
            return numeric
    return None


def _string_value(value: object) -> str | None:
    if isinstance(value, str) and value:
        return value
    if isinstance(value, int):
        return str(value)
    return None


def _infer_family_from_action_id(action_id: str, default_key: str | None) -> str:
    if action_id == "cloud":
        return "vertical"
    if action_id == "local":
        return "local"
    if action_id.isdigit():
        return "horizontal"
    if default_key is not None:
        if default_key in {"local", "horizontal", "vertical"}:
            return default_key
        if default_key == "cloud":
            return "vertical"
    return action_family(action_id)


def _candidate_delay_value(
    observation: Mapping[str, object],
    payload: Mapping[str, object],
    action_id: str,
    family: str,
    component: str,
) -> float | None:
    numeric = _numeric(payload.get(component))
    if numeric is not None:
        return numeric

    estimates = observation.get("queue_delay_estimates")
    if isinstance(estimates, Mapping):
        estimate = estimates.get(action_id, estimates.get(family))
        if isinstance(estimate, Mapping):
            numeric = _numeric(estimate.get(component))
        else:
            numeric = _numeric(estimate) if component == "queue_delay" else None
        if numeric is not None:
            return numeric

    if component == "queue_delay":
        value = observation.get(f"{action_id}_queue_delay", observation.get(f"{family}_{component}"))
    else:
        value = observation.get(f"{action_id}_{component}", observation.get(f"{family}_{component}"))
    return _numeric(value)


def _candidate_total_delay(
    observation: Mapping[str, object],
    payload: Mapping[str, object],
    action_id: str,
    family: str,
    queue_delay: float | None,
    transmission_delay: float | None,
    compute_delay: float | None,
) -> float | None:
    explicit = _numeric(payload.get("total_delay"))
    if explicit is not None:
        return explicit
    estimates = observation.get("queue_delay_estimates")
    if isinstance(estimates, Mapping):
        estimate = estimates.get(action_id, estimates.get(family))
        if isinstance(estimate, Mapping):
            explicit = _numeric(estimate.get("total_delay"))
            if explicit is not None:
                return explicit
    latency_estimates = observation.get("latency_estimates")
    if isinstance(latency_estimates, Mapping):
        estimate = _numeric(latency_estimates.get(action_id, latency_estimates.get(family)))
        if estimate is not None:
            return estimate
    load = _numeric(observation.get(f"{family}_destination_load") or observation.get("destination_load"))
    propagation = _numeric(observation.get(f"{family}_propagation_delay") or observation.get("propagation_delay"))
    explicit = _numeric(observation.get(f"{action_id}_total_delay", observation.get(f"{family}_total_delay")))
    if explicit is not None:
        return explicit
    components = tuple(
        component
        for component in (queue_delay, transmission_delay, propagation, compute_delay, load)
        if component is not None
    )
    if components:
        return float(sum(components))
    return None


def _fallback_reason(candidates: list[DelayCandidate] | tuple[DelayCandidate, ...]) -> str:
    if not candidates:
        return "no delay candidates could be built"
    if not any(candidate.available for candidate in candidates):
        return "no delay candidates are available under the legal action mask"
    return "no available delay candidates have comparable total delay"


def _fallback_from_hints(context: PolicyContext) -> str | None:
    hints = context.observation.get("fallback_hints")
    if not isinstance(hints, Mapping):
        return None
    legal = set(legal_actions(context))
    ranked: list[tuple[float, int, str]] = []
    for action in legal:
        family = action_family(action)
        score = _numeric(hints.get(action, hints.get(family)))
        if score is not None:
            ranked.append((score, _LEGACY_FAMILY_TIE_ORDER.get(family, len(_LEGACY_FAMILY_TIE_ORDER)), action))
    if not ranked:
        return None
    ranked.sort(key=lambda item: item[:2])
    return ranked[0][2]
