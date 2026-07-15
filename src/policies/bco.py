from __future__ import annotations

from dataclasses import dataclass

from .common import fallback_action, legal_actions
from .interface import PolicyContext, SharedPolicy


@dataclass(slots=True)
class BalancedCooperationOffloadingPolicy(SharedPolicy):
    policy_name: str = "BCO"
    balance_weight: float = 1.0

    def _load_score(self, context: PolicyContext, action: str) -> float:
        observation = context.observation
        local_wait = float(observation.get("private_wait_time", 0.0))
        offload_wait = float(observation.get("offload_wait_time", 0.0))
        history = float(len(context.trace_history))
        if action in {"local", "compute_local"}:
            return local_wait + self.balance_weight * history
        if action in {"horizontal", "offload_horizontal"}:
            return offload_wait + 0.5 * self.balance_weight * history
        if action in {"vertical", "offload_vertical"}:
            return offload_wait + 0.75 * self.balance_weight * history
        return float("inf")

    def choose_action(self, context: PolicyContext) -> str:
        legal = legal_actions(context)
        if not legal:
            raise ValueError("No legal actions available")
        scores = {action: self._load_score(context, action) for action in legal}
        best = min(scores.values())
        best_actions = sorted(action for action, score in scores.items() if score == best)
        return best_actions[0]
