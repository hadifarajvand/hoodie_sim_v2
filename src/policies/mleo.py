from __future__ import annotations

from dataclasses import dataclass

from .common import fallback_action, legal_actions
from .interface import PolicyContext, SharedPolicy


@dataclass(slots=True)
class MinimumLatencyEstimateOffloadingPolicy(SharedPolicy):
    policy_name: str = "MLEO"
    local_compute_rate: float = 1.0
    horizontal_transmission_cost: float = 1.2
    vertical_transmission_cost: float = 1.5
    queue_weight: float = 1.0

    def _estimate(self, context: PolicyContext, action: str) -> float:
        observation = context.observation
        task_size = float(observation.get("task_size", 0.0))
        processing_density = float(observation.get("processing_density", 0.0))
        private_wait = float(observation.get("private_wait_time", 0.0))
        offload_wait = float(observation.get("offload_wait_time", 0.0))
        causal_history = float(len(context.trace_history))
        compute = task_size * processing_density / max(self.local_compute_rate, 1e-6)
        if action in {"local", "compute_local"}:
            return private_wait + compute + 0.1 * causal_history
        if action in {"horizontal", "offload_horizontal"}:
            return offload_wait + self.horizontal_transmission_cost + compute + self.queue_weight * causal_history
        if action in {"vertical", "offload_vertical"}:
            return offload_wait + self.vertical_transmission_cost + compute + 0.5 * self.queue_weight * causal_history
        return float("inf")

    def choose_action(self, context: PolicyContext) -> str:
        legal = legal_actions(context)
        if not legal:
            raise ValueError("No legal actions available")
        estimates = {action: self._estimate(context, action) for action in legal}
        best = min(estimates.values())
        best_actions = sorted(action for action, estimate in estimates.items() if estimate == best)
        return best_actions[0]
