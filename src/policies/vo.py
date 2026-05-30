from __future__ import annotations

from .common import first_legal_action, placement_action
from .policy_interface import PolicyContext, SharedPolicy


class VerticalOffloadingPolicy(SharedPolicy):
    def choose_action(self, context: PolicyContext) -> str:
        concrete = placement_action(context, "vertical")
        if concrete is not None and context.legal_action_mask.get(concrete, False):
            return concrete
        return first_legal_action(context, ("vertical", "offload_vertical", "local", "compute_local"))
