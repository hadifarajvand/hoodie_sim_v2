from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .adaptive_context import AdaptiveDecisionContext, build_adaptive_context
from .common import legal_actions
from .policy_interface import PolicyContext, SharedPolicy


_CANONICAL_ORDER = (
    "local",
    "compute_local",
    "horizontal",
    "offload_horizontal",
    "vertical",
    "offload_vertical",
)


def _first_available(available: Iterable[str], preferred: tuple[str, ...]) -> str | None:
    available_set = set(available)
    for action in preferred:
        if action in available_set:
            return action
    return None


def _family(action: str) -> str:
    if action in {"local", "compute_local"}:
        return "local"
    if action in {"horizontal", "offload_horizontal"}:
        return "horizontal"
    if action in {"vertical", "offload_vertical"}:
        return "vertical"
    return action


def _canonical_index(action: str) -> int:
    try:
        return _CANONICAL_ORDER.index(action)
    except ValueError:
        return len(_CANONICAL_ORDER)


def _numeric_signal(*values: object) -> float | None:
    for value in values:
        if isinstance(value, (int, float)):
            return float(value)
    return None


def _effective_load(context: AdaptiveDecisionContext) -> float:
    queue_load = float(context.queue_load or 0.0)
    observed = float(context.observed_arrival_probability or 0.0)
    slack = None
    if context.absolute_deadline_slot is not None and context.current_slot is not None:
        slack = max(1, context.absolute_deadline_slot - context.current_slot)
    pressure = None
    if context.cycles_remaining is not None and slack is not None:
        pressure = float(context.cycles_remaining) / float(slack)
    candidates = [observed, queue_load / max(1.0, float(context.arrivals_per_slot and len(context.arrivals_per_slot) or 1))]
    if pressure is not None:
        candidates.append(pressure)
    return max(candidates) if candidates else 0.0


def _family_preference(context: AdaptiveDecisionContext) -> tuple[str, str, str]:
    load = _effective_load(context)
    if load <= 0.33:
        return ("local", "horizontal", "vertical")
    if load >= 0.75:
        return ("horizontal", "vertical", "local")
    return ("local", "horizontal", "vertical")


@dataclass(slots=True)
class AdaptiveOffloadingPolicy(SharedPolicy):
    def choose_action(self, context: PolicyContext) -> str:
        adaptive_context = build_adaptive_context(
            context,
            traffic_summary=context.observation.get("traffic_summary") if isinstance(context.observation, dict) else None,
            execution_summary=context.observation.get("execution_summary") if isinstance(context.observation, dict) else None,
        )
        legal = legal_actions(context)
        if not legal:
            raise ValueError("No legal actions available")

        legal_set = set(legal)
        preferred = _family_preference(adaptive_context)

        ranked: list[tuple[tuple[float, float, float, int], str]] = []
        for action in legal:
            family = _family(action)
            family_rank = float(preferred.index(family)) if family in preferred else float(len(preferred))
            latency_estimates = adaptive_context.latency_estimates or {}
            balance_hint = adaptive_context.balance_hint or {}
            fallback_hints = adaptive_context.observation.get("fallback_hints", {})
            metric = _numeric_signal(
                latency_estimates.get(action),
                latency_estimates.get(family),
                balance_hint.get(action),
                balance_hint.get(family),
                fallback_hints.get(action),
                fallback_hints.get(family),
            )
            if metric is None:
                metric = {"local": 1.0, "horizontal": 2.0, "vertical": 3.0}.get(family, 4.0)
            cycles_remaining = float(adaptive_context.cycles_remaining or adaptive_context.cycles_required or 0.0)
            deadline_slack = None
            if adaptive_context.absolute_deadline_slot is not None and adaptive_context.current_slot is not None:
                deadline_slack = max(0, adaptive_context.absolute_deadline_slot - adaptive_context.current_slot)
            urgency = cycles_remaining / float(max(1, deadline_slack or 1))
            ranked.append(
                (
                    (
                        family_rank,
                        metric,
                        -float(urgency if family != "local" else 0.0),
                        float(_canonical_index(action)),
                    ),
                    action,
                )
            )

        ranked.sort(key=lambda item: item[0])
        for _score, action in ranked:
            if action in legal_set:
                return action

        fallback = _first_available(legal, _family_preference(adaptive_context) + _CANONICAL_ORDER)
        if fallback is not None:
            return fallback

        return legal[0]
