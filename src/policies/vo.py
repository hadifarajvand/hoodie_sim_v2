from __future__ import annotations

from .common import first_legal_family_action, fallback_action
from .interface import PolicyContext, SharedPolicy


class VerticalOffloadingPolicy(SharedPolicy):
    policy_name = "VO"

    def choose_action(self, context: PolicyContext) -> str:
        return first_legal_family_action(context, "vertical") or fallback_action(context)
