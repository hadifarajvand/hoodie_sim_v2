from __future__ import annotations

from .common import fallback_action, legal_actions
from .interface import PolicyContext, SharedPolicy


class BalancedCooperationOffloadingPolicy(SharedPolicy):
    policy_name = "BCO"

    def choose_action(self, context: PolicyContext) -> str:
        legal = legal_actions(context)
        if not legal:
            raise ValueError("No legal actions available")
        return legal[0] if "local" in legal else fallback_action(context)
