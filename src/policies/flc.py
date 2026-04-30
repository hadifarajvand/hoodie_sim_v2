from __future__ import annotations

from .common import first_legal_action
from .policy_interface import PolicyContext, SharedPolicy


class FullLocalComputingPolicy(SharedPolicy):
    def choose_action(self, context: PolicyContext) -> str:
        action = first_legal_action(context, ("local", "compute_local"))
        if action not in {"local", "compute_local"}:
            raise ValueError("Local execution is not legal for the current task")
        return action
