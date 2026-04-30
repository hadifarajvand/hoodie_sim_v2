from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class DuelingDQN:
    value_weight: float = 1.0
    advantage_weights: dict[str, float] = field(default_factory=dict)

    def q_values(self, features: dict[str, float], legal_actions: tuple[str, ...]) -> dict[str, float]:
        state_value = self.value_weight * features.get("state_value", 0.0)
        if not legal_actions:
            return {}
        advantages = {action: self.advantage_weights.get(action, 0.0) for action in legal_actions}
        mean_advantage = sum(advantages.values()) / len(advantages)
        return {action: state_value + advantage - mean_advantage for action, advantage in advantages.items()}
