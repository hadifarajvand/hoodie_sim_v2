from __future__ import annotations

from .common import fallback_action
from .interface import PolicyContext, SharedPolicy


class FullLocalComputingPolicy(SharedPolicy):
    policy_name = "FLC"

    def choose_action(self, context: PolicyContext) -> str:
        return fallback_action(context)
