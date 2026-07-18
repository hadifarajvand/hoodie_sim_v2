from __future__ import annotations

from dataclasses import dataclass
from .common import (
    FALLBACK_FAMILY_ORDER,
    first_legal_family_action,
    legal_actions,
    placement_actions_for_family,
    placement_contract_available,
)
from .policy_interface import PolicyContext, SharedPolicy


@dataclass(slots=True)
class BalancedCooperationOffloadingPolicy(SharedPolicy):
    _next_family_index: int = 0
    _next_placement_index: int = 0

    def choose_action(self, context: PolicyContext) -> str:
        legal = legal_actions(context)
        if not legal:
            raise ValueError("No legal actions available")

        # The HOODIE paper baseline is a cyclic offloader.  Queue/load hints
        # belong to learned or latency-estimation policies and must not silently
        # turn BCO into a load-aware heuristic.
        if placement_contract_available(context):
            placements = self._ordered_placements(context)
            if placements:
                index = self._next_placement_index % len(placements)
                action = placements[index]
                self._next_placement_index = (index + 1) % len(placements)
                return action

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
    def _ordered_placements(context: PolicyContext) -> tuple[str, ...]:
        placements: list[str] = []
        for family in ("local", "vertical", "horizontal"):
            for action in placement_actions_for_family(context, family):
                if action not in placements:
                    placements.append(action)
        return tuple(placements)
