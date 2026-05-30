from __future__ import annotations

from .common import first_legal_action, placement_action
from .policy_interface import PolicyContext, SharedPolicy


class FullLocalComputingPolicy(SharedPolicy):
    def choose_action(self, context: PolicyContext) -> str:
        concrete = placement_action(context, "local")
        if concrete is not None and context.legal_action_mask.get(concrete, False):
            return concrete
        action = first_legal_action(context, ("local", "compute_local"))
        if action not in {"local", "compute_local"}:
            raise ValueError("Local execution is not legal for the current task")
        return action
