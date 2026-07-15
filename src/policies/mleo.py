from __future__ import annotations

from .common import first_legal_family_action, fallback_action
from .interface import PolicyContext, SharedPolicy


class MinimumLatencyEstimateOffloadingPolicy(SharedPolicy):
    policy_name = "MLEO"

    def choose_action(self, context: PolicyContext) -> str:
        for family in ("local", "horizontal", "vertical"):
            chosen = first_legal_family_action(context, family)
            if chosen is not None:
                return chosen
        return fallback_action(context)
