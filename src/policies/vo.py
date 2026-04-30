from __future__ import annotations

from .common import first_legal_action
from .policy_interface import PolicyContext, SharedPolicy


class VerticalOffloadingPolicy(SharedPolicy):
    def choose_action(self, context: PolicyContext) -> str:
        action = first_legal_action(context, ("vertical", "offload_vertical"))
        if action not in {"vertical", "offload_vertical"}:
            raise ValueError("Vertical offloading is not legal for the current task")
        return action
