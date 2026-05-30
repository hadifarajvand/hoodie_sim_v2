from __future__ import annotations

from dataclasses import dataclass, field

from .common import horizontal_destinations, legal_actions, source_agent_id
from .policy_interface import PolicyContext, SharedPolicy


@dataclass(slots=True)
class BalancedCooperationOffloadingPolicy(SharedPolicy):
    rollover_index: int = 0

    def choose_action(self, context: PolicyContext) -> str:
        source = source_agent_id(context)
        ordered: list[str] = []
        if context.legal_action_mask.get("local", False) or context.legal_action_mask.get("compute_local", False):
            ordered.extend(action for action in ("local", "compute_local") if context.legal_action_mask.get(action, False))
        if context.legal_action_mask.get("cloud", False) or context.legal_action_mask.get("vertical", False) or context.legal_action_mask.get("offload_vertical", False):
            ordered.extend(action for action in ("cloud", "vertical", "offload_vertical") if context.legal_action_mask.get(action, False))
        destinations = tuple(
            destination
            for destination in (
                horizontal_destinations(context)
                or tuple(action for action in legal_actions(context) if action not in {"local", "compute_local", "cloud", "vertical", "offload_vertical", "horizontal", "offload_horizontal"})
            )
            if destination != source and context.legal_action_mask.get(destination, False)
        )
        ordered.extend(destinations)
        if not ordered:
            raise ValueError("No legal actions available")
        index = self.rollover_index % len(ordered)
        self.rollover_index = (self.rollover_index + 1) % len(ordered)
        return ordered[index]
