from __future__ import annotations

from .policy_interface import PolicyContext


def build_legal_action_mask(allowed_actions: tuple[str, ...]) -> dict[str, bool]:
    return {action: True for action in allowed_actions}


def select_legal_action(context: PolicyContext, action: str) -> str:
    if action in ("local", "compute_local"):
        if not (context.legal_action_mask.get("local", False) or context.legal_action_mask.get("compute_local", False)):
            raise ValueError(f"Illegal action: {action}")
    elif action.startswith("horizontal_") or action in ("horizontal", "offload_horizontal"):
        if not (context.legal_action_mask.get("horizontal", False) or context.legal_action_mask.get("offload_horizontal", False)):
            raise ValueError(f"Illegal action: {action}")
    elif action in ("cloud", "vertical", "offload_vertical"):
        if not (context.legal_action_mask.get("vertical", False) or context.legal_action_mask.get("offload_vertical", False) or context.legal_action_mask.get("cloud", False)):
            raise ValueError(f"Illegal action: {action}")
    elif not context.legal_action_mask.get(action, False):
        raise ValueError(f"Illegal action: {action}")
    return action
