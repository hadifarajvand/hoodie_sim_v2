from __future__ import annotations

from .common import first_legal_action
from .policy_interface import PolicyContext, SharedPolicy


class HorizontalOffloadingPolicy(SharedPolicy):
    def choose_action(self, context: PolicyContext) -> str:
        action = first_legal_action(context, ("horizontal", "offload_horizontal"))
        if action not in {"horizontal", "offload_horizontal"}:
            raise ValueError("Horizontal offloading is not legal for the current task")
        return action
