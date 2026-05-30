from __future__ import annotations

from .common import horizontal_destinations, source_agent_id
from .policy_interface import PolicyContext, SharedPolicy


class HorizontalOffloadingPolicy(SharedPolicy):
    def choose_action(self, context: PolicyContext) -> str:
        source = source_agent_id(context)
        destinations = horizontal_destinations(context)
        if source is not None and destinations:
            legal_destinations = tuple(destination for destination in destinations if destination != source and context.legal_action_mask.get(destination, False))
            if legal_destinations:
                return legal_destinations[0]
        if context.legal_action_mask.get("horizontal", False):
            return "horizontal"
        if context.legal_action_mask.get("offload_horizontal", False):
            return "offload_horizontal"
        if context.legal_action_mask.get("local", False):
            return "local"
        if context.legal_action_mask.get("compute_local", False):
            return "compute_local"
        raise ValueError("Horizontal offloading is not legal for the current task")
