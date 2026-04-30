from __future__ import annotations

from typing import Iterable

from .policy_interface import PolicyContext


def legal_actions(context: PolicyContext) -> tuple[str, ...]:
    return tuple(action for action, allowed in context.legal_action_mask.items() if allowed)


def first_legal_action(context: PolicyContext, preferred: Iterable[str]) -> str:
    legal = legal_actions(context)
    legal_set = set(legal)
    for action in preferred:
        if action in legal_set:
            return action
    if not legal:
        raise ValueError("No legal actions available")
    return legal[0]

