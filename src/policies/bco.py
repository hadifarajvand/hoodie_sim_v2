from __future__ import annotations

from dataclasses import dataclass

from .common import FALLBACK_FAMILY_ORDER, action_family, first_legal_family_action, legal_actions
from .policy_interface import PolicyContext, SharedPolicy


@dataclass(slots=True)
class BalancedCooperationOffloadingPolicy(SharedPolicy):
    _next_family_index: int = 0

    def choose_action(self, context: PolicyContext) -> str:
        legal = legal_actions(context)
        if not legal:
            raise ValueError("No legal actions available")

        hint = context.observation.get("balance_hint")
        if isinstance(hint, dict):
            ranked: list[tuple[float, int, str]] = []
            for action in legal:
                score = hint.get(action, hint.get(action_family(action)))
                if isinstance(score, (int, float)):
                    ranked.append((float(score), self._family_order_index(action_family(action)), action))
            if ranked:
                ranked.sort(key=lambda item: item[:2])
                return ranked[0][2]

        family_count = len(FALLBACK_FAMILY_ORDER)
        for offset in range(family_count):
            index = (self._next_family_index + offset) % family_count
            family = FALLBACK_FAMILY_ORDER[index]
            action = first_legal_family_action(context, family)
            if action is not None:
                self._next_family_index = (index + 1) % family_count
                return action
        raise ValueError("No legal actions available")

    @staticmethod
    def _family_order_index(family: str) -> int:
        try:
            return FALLBACK_FAMILY_ORDER.index(family)
        except ValueError:
            return len(FALLBACK_FAMILY_ORDER)
