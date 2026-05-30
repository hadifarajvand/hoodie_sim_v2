from __future__ import annotations

from .common import fallback_action, first_legal_placement_action
from .policy_interface import PolicyContext, SharedPolicy


class VerticalOffloadingPolicy(SharedPolicy):
    def choose_action(self, context: PolicyContext) -> str:
        preferred = first_legal_placement_action(context, "vertical")
        if preferred is not None:
            return preferred
        return fallback_action(context)
