from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping

from .common import (
    action_family,
    fallback_action,
    first_legal_family_action,
    legal_actions,
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
    tie_break_key: tuple[int, str] = (0, "")
    fallback_notes: str | None = None


_FAMILY_TIE_ORDER = {"local": 0, "horizontal": 1, "vertical": 2}


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
    observation = context.observation if isinstance(context.observation, dict) else {}
    legal = set(legal_actions(context))
    candidates: list[DelayCandidate] = []
    for family in ("local", "horizontal", "vertical"):
        action_id = _candidate_action_id(context, observation, family)
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
                tie_break_key=(_FAMILY_TIE_ORDER[family], action_id),
                fallback_notes=notes,
            )
        )
    return tuple(candidates)


def _candidate_action_id(context: PolicyContext, observation: Mapping[str, object], family: str) -> str:
    candidate_payload = _candidate_payload(observation, family)
    if isinstance(candidate_payload, Mapping):
        action_id = candidate_payload.get("action_id")
        if isinstance(action_id, str) and action_id:
            return action_id
    preferred = first_legal_family_action(context, family)
    if preferred is not None:
        return preferred
    return {"local": "local", "horizontal": "horizontal", "vertical": "vertical"}[family]


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
    components = (queue_delay, transmission_delay, compute_delay)
    if all(component is not None for component in components):
        return float(sum(component for component in components if component is not None))
    return None


def _numeric(value: object) -> float | None:
    if isinstance(value, (int, float)):
        numeric = float(value)
        if isfinite(numeric):
            return numeric
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
            ranked.append((score, _FAMILY_TIE_ORDER.get(family, len(_FAMILY_TIE_ORDER)), action))
    if not ranked:
        return None
    ranked.sort(key=lambda item: item[:2])
    return ranked[0][2]
