from __future__ import annotations

from collections.abc import Mapping, Sequence

from .common import legal_actions
from .policy_interface import PolicyContext, SharedPolicy

_LEGAL_FALLBACK_ORDER = ("local", "compute_local", "horizontal", "offload_horizontal", "vertical", "offload_vertical")


class DALShadowPolicy(SharedPolicy):
    """Deterministic opt-in policy that consumes DAL advisories as read-only input."""

    def choose_action(self, context: PolicyContext) -> str:
        legal = tuple(legal_actions(context))
        legal_set = set(legal)
        advisory = _mapping_or_none(context.dal_advisory)
        if advisory is not None:
            deadline_pressure = str(advisory.get("deadline_pressure", "none")).strip().lower()
            queue_pressure = _queue_pressure_score(advisory)
            if deadline_pressure in {"expired", "critical", "high"}:
                preferred = ("local", "compute_local", "horizontal", "offload_horizontal", "vertical", "offload_vertical")
                action = _first_legal(preferred, legal_set)
                if action is not None:
                    return action
            if queue_pressure > 0 and deadline_pressure in {"low", "medium", "none"}:
                preferred = ("vertical", "offload_vertical", "horizontal", "offload_horizontal", "local", "compute_local")
                action = _first_legal(preferred, legal_set)
                if action is not None:
                    return action
        action = _first_legal(_LEGAL_FALLBACK_ORDER, legal_set)
        if action is not None:
            return action
        if not legal:
            raise ValueError("No legal actions available")
        return legal[0]


def _mapping_or_none(value: object) -> Mapping[str, object] | None:
    if isinstance(value, Mapping):
        return value
    return None


def _queue_pressure_score(advisory: Mapping[str, object]) -> int:
    total = 0
    for key in ("private_queue_load", "offloading_queue_load", "public_queue_load", "total_queue_load"):
        value = advisory.get(key)
        if isinstance(value, int):
            total += value
    return total


def _first_legal(preferred: Sequence[str], legal_set: set[str]) -> str | None:
    for action in preferred:
        if action in legal_set:
            return action
    return None
