from __future__ import annotations

from .policy_interface import PolicyContext


def build_legal_action_mask(allowed_actions: tuple[str, ...]) -> dict[str, bool]:
    return {action: True for action in allowed_actions}


def select_legal_action(context: PolicyContext, action: str) -> str:
    if not context.legal_action_mask.get(action, False):
        raise ValueError(f"Illegal action: {action}")
    return action
