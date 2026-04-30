from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DoubleDQNSelector:
    def select_action(self, online_q_values: dict[str, float], legal_actions: tuple[str, ...]) -> str:
        if not legal_actions:
            raise ValueError("No legal actions available")
        return max(legal_actions, key=lambda action: online_q_values.get(action, float("-inf")))

    def target_value(self, online_q_values: dict[str, float], target_q_values: dict[str, float], legal_actions: tuple[str, ...]) -> float:
        chosen_action = self.select_action(online_q_values, legal_actions)
        return target_q_values.get(chosen_action, 0.0)
