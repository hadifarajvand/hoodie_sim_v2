from __future__ import annotations

from typing import Iterable

from .policy_interface import PolicyContext

LOCAL_ACTIONS = ("local", "compute_local")
HORIZONTAL_ACTIONS = ("horizontal", "offload_horizontal")
VERTICAL_ACTIONS = ("vertical", "offload_vertical")
FAMILY_ACTIONS = {
    "local": LOCAL_ACTIONS,
    "horizontal": HORIZONTAL_ACTIONS,
    "vertical": VERTICAL_ACTIONS,
}
FALLBACK_FAMILY_ORDER = ("local", "horizontal", "vertical")
FALLBACK_ACTION_ORDER = LOCAL_ACTIONS + HORIZONTAL_ACTIONS + VERTICAL_ACTIONS


def action_family(action: str) -> str:
    for family, actions in FAMILY_ACTIONS.items():
        if action in actions:
            return family
    return action


def legal_actions(context: PolicyContext) -> tuple[str, ...]:
    return tuple(action for action, allowed in context.legal_action_mask.items() if allowed)


def first_legal_action(context: PolicyContext, preferred: Iterable[str] = FALLBACK_ACTION_ORDER) -> str:
    legal = legal_actions(context)
    legal_set = set(legal)
    for action in preferred:
        if action in legal_set:
            return action
    if not legal:
        raise ValueError("No legal actions available")
    return legal[0]


def first_legal_family_action(context: PolicyContext, family: str) -> str | None:
    return first_legal_from_actions(context, FAMILY_ACTIONS.get(family, (family,)))


def first_legal_from_actions(context: PolicyContext, preferred: Iterable[str]) -> str | None:
    legal_set = set(legal_actions(context))
    for action in preferred:
        if action in legal_set:
            return action
    return None


def fallback_action(context: PolicyContext) -> str:
    """Documented fallback: local, then horizontal, then vertical, then mask order."""
    return first_legal_action(context, FALLBACK_ACTION_ORDER)


def legal_family_available(context: PolicyContext, family: str) -> bool:
    return first_legal_family_action(context, family) is not None
