from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping

from .common import (
    FALLBACK_FAMILY_ORDER,
    action_family,
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
        observation = context.observation if isinstance(context.observation, Mapping) else {}
        load_hint = observation.get("balance_hint")
        if isinstance(load_hint, Mapping):
            ranked: list[tuple[float, int, str]] = []
            for action in legal:
                family = action_family(action)
                score = load_hint.get(action, load_hint.get(family, load_hint.get(family.upper())))
                if isinstance(score, (int, float)):
                    ranked.append((float(score), self._family_order_index(family), action))
            if ranked:
                ranked.sort(key=lambda item: (item[0], item[1], item[2]))
                return ranked[0][2]

        family_scores = self._family_scores(observation)
        if any(score != 0.0 for score in family_scores.values()):
            ranked_families = sorted(family_scores.items(), key=lambda item: (item[1], self._family_order_index(item[0]), item[0]))
            for family, _score in ranked_families:
                action = first_legal_family_action(context, family)
                if action is not None:
                    return action

        family_count = len(FALLBACK_FAMILY_ORDER)
        for offset in range(family_count):
            index = (self._next_family_index + offset) % family_count
            family = FALLBACK_FAMILY_ORDER[index]
            action = first_legal_family_action(context, family)
            if action is not None:
                self._next_family_index = (index + 1) % family_count
                return action

        if placement_contract_available(context):
            placements = self._ordered_placements(context)
            if placements:
                index = self._next_placement_index % len(placements)
                action = placements[index]
                self._next_placement_index = (index + 1) % len(placements)
                return action
        raise ValueError("No legal actions available")

    @staticmethod
    def _family_scores(observation: Mapping[str, object]) -> dict[str, float]:
        scores = {"local": 0.0, "horizontal": 0.0, "vertical": 0.0}
        for family in scores:
            queue = observation.get(f"{family}_queue") or observation.get(f"{family}_queue_length") or observation.get(f"{family}_load")
            if isinstance(queue, (int, float)):
                scores[family] += float(queue)
        if isinstance(observation.get("queue_load"), (int, float)):
            shared = float(observation["queue_load"])
            scores["horizontal"] += shared
            scores["vertical"] += shared
        if isinstance(observation.get("destination_loads"), Mapping):
            for family in scores:
                value = observation["destination_loads"].get(family)
                if isinstance(value, (int, float)):
                    scores[family] += float(value)
        return scores

    @staticmethod
    def _family_order_index(family: str) -> int:
        try:
            return FALLBACK_FAMILY_ORDER.index(family)
        except ValueError:
            return len(FALLBACK_FAMILY_ORDER)

    @staticmethod
    def _ordered_placements(context: PolicyContext) -> tuple[str, ...]:
        placements: list[str] = []
        for family in ("local", "vertical", "horizontal"):
            for action in placement_actions_for_family(context, family):
                if action not in placements:
                    placements.append(action)
        return tuple(placements)
