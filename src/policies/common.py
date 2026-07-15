from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Iterable

from .interface import PolicyContext

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


def legal_actions(context: PolicyContext) -> tuple[str, ...]:
    return tuple(action for action, allowed in context.legal_action_mask.items() if allowed)


def fallback_action(context: PolicyContext) -> str:
    legal = legal_actions(context)
    if not legal:
        raise ValueError("No legal actions available")
    for action in FALLBACK_ACTION_ORDER:
        if action in legal:
            return action
    return legal[0]


def first_legal_family_action(context: PolicyContext, family: str) -> str | None:
    legal = set(legal_actions(context))
    for action in FAMILY_ACTIONS.get(family, (family,)):
        if action in legal:
            return action
    return None


def first_legal_placement_action(context: PolicyContext, family: str) -> str | None:
    return first_legal_family_action(context, family)


def placement_actions_for_family(context: PolicyContext, family: str) -> tuple[str, ...]:
    action = first_legal_family_action(context, family)
    return () if action is None else (action,)
