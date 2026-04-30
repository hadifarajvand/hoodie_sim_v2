from __future__ import annotations

from .common import first_legal_action, legal_actions
from .policy_interface import PolicyContext, SharedPolicy


class MinimumLatencyEstimateOffloadingPolicy(SharedPolicy):
    def choose_action(self, context: PolicyContext) -> str:
        estimates = context.observation.get("latency_estimates", {})
        legal = legal_actions(context)
        if isinstance(estimates, dict):
            ranked = sorted(
                ((action, estimates.get(action)) for action in legal),
                key=lambda item: (item[1] is None, item[1]),
            )
            for action, estimate in ranked:
                if estimate is not None:
                    return action
        return first_legal_action(context, ("offload", "horizontal", "vertical", "local"))

