from __future__ import annotations

from .common import first_legal_action, legal_actions
from .policy_interface import PolicyContext, SharedPolicy


class BalancedCooperationOffloadingPolicy(SharedPolicy):
    def choose_action(self, context: PolicyContext) -> str:
        hint = context.observation.get("balance_hint")
        legal = legal_actions(context)
        if isinstance(hint, dict):
            ranked = sorted(
                ((action, hint.get(action)) for action in legal),
                key=lambda item: (item[1] is None, item[1]),
            )
            for action, score in ranked:
                if score is not None:
                    return action
        return first_legal_action(context, ("local", "horizontal", "vertical", "offload"))

