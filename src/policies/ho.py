from __future__ import annotations

from .common import first_legal_placement_action, fallback_action
from .interface import PolicyContext, SharedPolicy


class HorizontalOffloadingPolicy(SharedPolicy):
    policy_name = "HO"

    def choose_action(self, context: PolicyContext) -> str:
        return first_legal_placement_action(context, "horizontal") or fallback_action(context)
